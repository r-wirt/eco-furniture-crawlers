# -*- coding: utf-8 -*-
from scrapy import Spider
from proto_spider.items import productSpiderItem
from scrapy.http import Request
import ast

class PotterybarnkidsSpider(Spider):
    name = 'potterybarnkids'
    custom_settings = {'ELASTICSEARCH_INDEX': 'potterybarnkids'}
    allowed_domains = ['potterybarnkids.com']
    start_urls = ['https://www.potterybarnkids.com/shop/featured-shops/greenguard-feature/?cm_src=OLDLINK&searchredir=true&term=greenguard']

    def parse(self, response):
        #URL Links to each product within 'Greenguard Gold' results
        products = response.xpath("//div[@class='toolbox-for-product-cell']/a/@href").extract()
        for product in products:
            yield Request(product, callback=self.parse_product, dont_filter=True)

        #Begin processing next page
        absolute_next_page_url = response.xpath('//a[@id="nextPage"]/@href').extract_first()
        yield Request(absolute_next_page_url, callback=self.parse, dont_filter=True)

    def parse_product(self, response):

        productname = response.xpath('//div[@class="pip-summary"]/h1/text()').extract_first()
        product_url = response.xpath('//head/meta[@property="og:url"]/@content').extract_first()
        image = response.xpath('//head/meta[@property="og:image"]/@content').extract_first()
        #Description response will have unicode characters in scrapy shell but they are parsed into utf-8
        #when it is sent via ElasticSearch pipeline
        description = response.xpath('//head/meta[@property="twitter:description"]/@content').extract_first()
        #The following line will return the price(s) as a string in a list, and it may also have commas.
        original_price_span = response.xpath('//section[@class="simple-subset"]//span[@class="price-amount"]/text()').extract()

        #Some Pottery Barn Kids products list a price range for different sizes
        #Products with a price range must be grabbed from a different section on product page
        #This function is intended to remove any commas and turn the strings into integers
        #The function also grabs the low and high price if original_price_span is empty
        def modifyPriceList (thePriceSpan):

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

        #Most of the eco-products on Pottery Barn Kids products are Greenguard Gold Certified
        #Currently no FSC Products have been noted for this store
        certifications = [{
"certification": "GREENGUARD Certified",
"title": "GREENGUARD Certified products contain materials and finishes that have been verified to have low chemical emissions. \
 As a result, this product improves overall indoor air quality by reducing the presence of harmful \
 pollutants and airborne chemicals.", "url": "http://greenguard.org/en/CertificationPrograms/CertificationPrograms_indoorAirQuality.aspx"
}]
        #In order for elasticsearch to sort the products by price amount it will need the first
        #one in the array if there is a price range for the product
        lowest_price = final_price_span[0]

        load_item = productSpiderItem()

        load_item['sitename'] = 'Pottery Barn Kids'
        load_item['productname'] = productname
        load_item['producturl'] = product_url
        load_item['image'] = image
        load_item['price'] = final_price_span
        load_item['certifications'] = certifications
        load_item['description'] = description
        load_item['lowestprice'] = lowest_price
        #Returns object with each load_item included
        yield load_item
