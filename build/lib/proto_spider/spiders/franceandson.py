# -*- coding: utf-8 -*-
from scrapy import Spider
from proto_spider.items import productSpiderItem
from scrapy.http import Request

class FranceandsonSpider(Spider):
    name = 'franceandson'
    custom_settings = {'ELASTICSEARCH_INDEX': 'franceandson'}
    allowed_domains = ['franceandson.com']
    start_urls = ['https://www.franceandson.com/search?type=article%2Cpage%2Cproduct&q=fsc']

    def parse(self, response):
        #URL Links to each product within 'FSC' results
        products = response.xpath('//div[@class="productitem"]/a/@href').extract()
        for product in products:
            yield Request('https://www.franceandson.com' + product, callback=self.parse_product, dont_filter=True)
           #Begin processing next page
        absolute_next_page_url = 'https://www.franceandson.com' + response.xpath('//li[@class="pagination--next"]/a/@href').extract_first()
        yield Request(absolute_next_page_url, callback=self.parse, dont_filter=True)

    def parse_product(self, response):

        #Check the product page to see if it includes the sold out tag
        sold_out = response.xpath('//span[@class="product--badge badge--soldout"]/text()').extract()
        #If the page does contain sold out tag end the parse_product function
        if sold_out == []:
            return

        product_name = response.xpath('//meta[@property="og:title"]/@content').extract_first()
        product_url = response.xpath('//meta[@property="og:url"]/@content').extract_first()
        image = response.xpath('//meta[@property="og:image"]/@content').extract_first()
        description = response.xpath('//meta[@property="og:description"]/@content').extract_first()
        original_price = response.xpath('//meta[@property="og:price:amount"]/@content').extract_first()

        #The prices will be returned as a string, and they may also have commas in them,
        #This function is intended to remove any commas and turn the strings into integers
        def modifyPriceList (thePrice):
            price_container = []
            #Takes commas out of price
            price_without_commas = thePrice.replace(',','')
            #Turns price_without_commas into floating integer
            price_as_integer = float(price_without_commas)
            price_container.append(price_as_integer)
            return price_container

        final_price = modifyPriceList(original_price)
        #Most of the eco-products on France and Son are FSC Certified
        #Currently no Greenguard Products have been noted for this store
        certifications = [{"certification": "Forest Stewardship (FSC) Certified",
                          "title": "FSC Certified products help reduce deforestation by ensuring products have been manufactured with recycled wood materials or have originated from sustainably managed forests.",
                          "url": "https://us.fsc.org/en-us/what-we-do/mission-and-vision"}]


        load_item = productSpiderItem()

        load_item['sitename'] = 'France and Son'
        load_item['productname'] = product_name
        load_item['producturl'] = product_url
        load_item['image'] = image
        load_item['price'] = final_price
        load_item['certifications'] = certifications
        load_item['description'] = description
        load_item['lowestprice'] = final_price[0]
        #Returns object with each load_item included
        yield load_item
