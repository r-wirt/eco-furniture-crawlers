# -*- coding: utf-8 -*-
from scrapy import Spider
from proto_spider.items import productSpiderItem
from scrapy.http import Request
import ast

class PbteenSpider(Spider):
    name = 'pbteen'
    custom_settings = {'ELASTICSEARCH_INDEX': 'pbteen'}
    allowed_domains = ['pbteen.com']
    start_urls = ['https://www.pbteen.com/search/results.html?words=fsc&cm_sp=HeaderLinks-_-OnsiteSearch-_-MainSite&cm_type=OnsiteSearch']

    def parse(self, response):
        #URL Links to each product within 'FSC' results
        #***Important Note: PBTeen currently has only one page of results for 'FSC' products
        products = response.xpath("//div[@class='toolbox-for-product-cell']/a/@href").extract()
        for product in products:
            yield Request(product, callback=self.parse_product, dont_filter=True)


    def parse_product(self, response):

        productname = response.xpath('//div[@class="pip-summary"]/h1/text()').extract_first()
        product_url = response.xpath('//head/meta[@property="og:url"]/@content').extract_first()
        image = response.xpath('//head/meta[@property="og:image"]/@content').extract_first()
        #Description response will have unicode characters but the setting turns them back into utf-8
        #when it is sent via ElasticSearch pipeline
        description = response.xpath('//head/meta[@property="twitter:description"]/@content').extract_first()
        #The following line will return the price(s) as a string, and it may also have commas.
        original_price_span = response.xpath('//section[@class="simple-subset"]//span[@class="price-amount"]/text()').extract()

        #Some PBTeen products list a price range for different sizes
        #This function is intended to remove any commas and turn the strings into integers
        def modifyPriceList (thePriceSpan):

            #If the following condition is true
            #It indicates that a price range is in place for the product
            if thePriceSpan == []:
            
                price_container = []
                #Grabs the object as a string from script element on page
                #Object contains both high price and low price
                load_string_with_pricing = response.xpath('//script[@type="application/ld+json"]/text()').extract_first()
                #Converts string element to dictionary
                convert_string_to_dictionary = ast.literal_eval(load_string_with_pricing)
                #Grab highest and lowest price
                low_price = convert_string_to_dictionary['offers']['lowPrice']
                high_price = convert_string_to_dictionary['offers']['highPrice']
                #Add low price and high price to price_conteinr list
                price_container.extend([low_price, high_price])
                #Convert low price and high price to floating numbers
                price_container = list(map(float, price_container))
                return price_container

            #Whenever there are two numbers in the list
            #The first one has to be deleted because it is not
            #the current marked down price
            if len(thePriceSpan) == 2:
                del thePriceSpan[:1]

            #Removes original price range, and extracts the new marked down price range
            if len(thePriceSpan) == 4:
                del thePriceSpan[:2]

            price_container = []
            for price in thePriceSpan:
                #Takes commas out of price
                price_without_commas = price.replace(',','')
                price_container.append(price_without_commas)
            #Changes each number in price container to a floating number
            price_container = list(map(float, price_container))
            return price_container

        final_price_span = modifyPriceList(original_price_span)

        #Most of the eco-products on PBTeen are FSC Certified
        #Should check for more Greenguard Products in the future
        certifications = [{"certification": "Forest Stewardship (FSC) Certified",
                          "title": "FSC Certified products help reduce deforestation by ensuring products have been manufactured with recycled wood materials or have originated from sustainably managed forests.",
                          "url": "https://us.fsc.org/en-us/what-we-do/mission-and-vision"}]
        #In order for elasticsearch to sort the products by price amount it will need the first
        #one in the array if there is a price range for the product
        lowest_price = final_price_span[0]

        load_item = productSpiderItem()

        load_item['sitename'] = 'pbteen'
        load_item['productname'] = productname
        load_item['producturl'] = product_url
        load_item['image'] = image
        load_item['price'] = final_price_span
        load_item['certifications'] = certifications
        load_item['description'] = description
        load_item['lowestprice'] = lowest_price
        #Returns object with each load_item included
        yield load_item
