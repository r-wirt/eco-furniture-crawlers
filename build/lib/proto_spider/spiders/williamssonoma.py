# -*- coding: utf-8 -*-
from scrapy import Spider
from proto_spider.items import productSpiderItem
from scrapy.http import Request
import ast

class WilliamssonomaSpider(Spider):
    name = 'williamssonoma'
    custom_settings = {'ELASTICSEARCH_INDEX': 'williamssonoma'}
    allowed_domains = ['williamssonoma.com']
    #Collections with FSC Certified Materials on Williams-Sonoma:
    #Branden, Piedmont, Sussex, Trevor, Vienna
    start_urls = ['https://www.williams-sonoma.com/search/results.html?words=branden&cm_sp=HeaderLinks-_-OnsiteSearch-_-MainSite&cm_type=OnsiteSearch',
                  'https://www.williams-sonoma.com/search/results.html?words=piedmont&cm_sp=HeaderLinks-_-OnsiteSearch-_-MainSite&cm_type=OnsiteSearch',
                  'https://www.williams-sonoma.com/search/results.html?words=sussex&cm_sp=HeaderLinks-_-OnsiteSearch-_-MainSite&cm_type=OnsiteSearch',
                  'https://www.williams-sonoma.com/search/results.html?words=trevor&cm_sp=HeaderLinks-_-OnsiteSearch-_-MainSite&cm_type=OnsiteSearch',
                  'https://www.williams-sonoma.com/search/results.html?words=vienna&cm_sp=HeaderLinks-_-OnsiteSearch-_-MainSite&cm_type=OnsiteSearch']

    def parse(self, response):
        products = response.xpath('//div[@class="toolbox-for-product-cell"]/a/@href').extract()
        for product in products:
            yield Request(product, callback= self.parse_product, dont_filter=True)
        #Currently there are no next page urls required for this Spider

    def parse_product(self, response):
        #Check the products description section on the page to make sure it is FSC Certified
        check_for_fsc_cert = response.xpath('//div[@class="accordion-tab-copy"]//ul/li[text()[contains(.,"FSC")]]').extract()
        if check_for_fsc_cert == []:
            return
        product_name = response.xpath('//meta[@property="og:title"]/@content').extract_first()
        product_url = response.xpath('//meta[@property="og:url"]/@content').extract_first()
        image = response.xpath('//meta[@property="og:image"]/@content').extract_first()
        description = response.xpath('//meta[@name="description"]/@content').extract_first()
        original_price = response.xpath('//div[@class="pip-summary"]//span[@class="price-amount"]/text()').extract()

        def modifyPriceList(thePriceSpan):
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

        final_price = modifyPriceList(original_price)

        #Most of the eco-products on davincibaby are GREENGUARD Gold Certified
        certifications = [{"certification": "Forest Stewardship (FSC) Certified",
                          "title": "FSC Certified products help reduce deforestation by ensuring products have been manufactured with recycled wood materials or have originated from sustainably managed forests. For more information click here",
                          "url": "https://us.fsc.org/en-us/what-we-do/mission-and-vision"}]

        load_item = productSpiderItem()

        load_item['sitename'] = 'Williams Sonoma'
        load_item['productname'] = product_name
        load_item['producturl'] = product_url
        load_item['image'] = image
        load_item['price'] = final_price
        load_item['certifications'] = certifications
        load_item['description'] = description
        load_item['lowestprice'] = final_price[0]
        #Returns object with each load_item included
        yield load_item
