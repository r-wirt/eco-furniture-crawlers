# -*- coding: utf-8 -*-
from scrapy import Spider
from proto_spider.items import productSpiderItem
from scrapy.http import Request


class RominafurnitureSpider(Spider):
    name = 'rominafurniture'
    custom_settings = {'ELASTICSEARCH_INDEX': 'rominafurniture'}
    allowed_domains = ['rominafurniture.com']

    def start_requests(self):
        yield Request('https://rominafurniture.com/product-category/baby/',callback=self.parse, dont_filter=True)
        yield Request('https://rominafurniture.com/product-category/teen/',callback=self.parse, dont_filter=True)
        yield Request('https://rominafurniture.com/product-category/modern/',callback=self.parse, dont_filter=True)
        yield Request('https://rominafurniture.com/product-category/classic/',callback=self.parse, dont_filter=True)

    def parse(self, response):
        furniture_type = response.xpath('//div[@class="text-center m-t-20"]/a/@href').extract()
        for furnituretype in furniture_type:
            yield Request(furnituretype, callback=self.parse_furnituretype_page, dont_filter=True)


    def parse_furnituretype_page(self, response):
        product_link =  response.xpath('//div[@class="item"]/a/@href').extract()
        for product in product_link:
            yield Request(product, callback=self.parse_product, dont_filter=True)

    def parse_product(self, response):
        #Checking product description for Greenguard Gold, if no Greenguard Gold is
        #detected the function should be cancelled since the product may not be certified
        check_description = response.xpath('//div[@class="std"]//ul/li').extract()
        def check_for_certification(description):
            if any("GREENGUARD Gold" in string for string in description):
                pass
            else:
                return

        productname = response.xpath('//h1[@itemprop="name"]/text()').extract_first()
        product_url = response.xpath('//meta[@itemprop="url"]/@content').extract_first()
        image = response.xpath('//ul[@id="imageGallery"]/li//img/@src').extract_first()
        #.replace() Removes excess unicode characters
        description = response.xpath('//div[@class="std"]/p/text()').extract_first().replace(u'\xa0', u' ')
        #The price for the product changes dynamically at the last minute, this price may be off
        original_price = response.xpath('//span[@class="amount"]/text()').extract_first()

        #The prices will be returned as a string, and they may also have commas in them,
        #This function is intended to remove any commas and turn the strings into integers
        def modifyPriceList (thePrice):
            price_container = []
            #Takes commas and dollar signs out of price
            price_without_commas = thePrice.replace(',','').replace('$','')
            price_container.append(price_without_commas)
            #Changes each number in price container to a floating number
            price_container = list(map(float, price_container))
            return price_container

        final_price = modifyPriceList(original_price)
        certifications = [{
"certification": "GREENGUARD Certified",
"title": "GREENGUARD Certified products contain materials and finishes that have been verified to have low chemical emissions. \
 As a result, this product improves overall indoor air quality by reducing the presence of harmful \
 pollutants and airborne chemicals.", "url": "http://greenguard.org/en/CertificationPrograms/CertificationPrograms_indoorAirQuality.aspx"
}]


        load_item = productSpiderItem()

        load_item['sitename'] = 'Romina Furniture'
        load_item['productname'] = productname
        load_item['producturl'] = product_url
        load_item['image'] = image
        load_item['price'] = final_price
        load_item['certifications'] = certifications
        load_item['description'] = description
        load_item['lowestprice'] = final_price
        #Returns object with each load_item included
        yield load_item
