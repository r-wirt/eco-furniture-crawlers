# -*- coding: utf-8 -*-
from scrapy import Spider
from proto_spider.items import productSpiderItem
from scrapy.http import Request
import re

class RominafurnitureSpider(Spider):
    name = 'rominafurniture'
    custom_settings = {'ELASTICSEARCH_INDEX': 'rominafurniture'}
    allowed_domains = ['rominafurniture.com']

    def start_requests(self):
        yield Request('https://rominafurniture.com/collections/dressers-chests',callback=self.parse, dont_filter=True)
        # yield Request('https://rominafurniture.com/product-category/teen/',callback=self.parse, dont_filter=True)
        # yield Request('https://rominafurniture.com/product-category/modern/',callback=self.parse, dont_filter=True)
        # yield Request('https://rominafurniture.com/product-category/classic/',callback=self.parse, dont_filter=True)

    def parse(self, response):
        product_links = re.findall(r'href="([^"]*?)"\s*>\s*BUY\s*NOW\s*</a>', response.text, flags=re.I |re.S)
        for product_link in product_links:
            product_link = 'https://rominafurniture.com' + product_link
            yield Request(product_link, callback=self.parse_product, dont_filter=True)

    def parse_product(self, response):
        #Checking  for Greenguard Gold, if no Greenguard Cert is
        #detected close method
        greenguard_verified = re.search(r'<a\s*href="[^"]*?"\s*title="[^"]*?GREENGUARD[^"]*?"', response.text, flags=re.I |re.S)
        if not greenguard_verified:
            print("No Greenguard Products Detected")
            return

        productname = re.search(r'itemprop="name"\s*content="([^"]*?)">', response.text, flags=re.I | re.S).group(1)
        product_url = response.xpath('//meta[@itemprop="url"]/@content').extract_first()
        image_url_stub = re.search(r'data-src="([^"]*?)"[^>]*?id="ProductPhotoImg">', response.text, flags=re.I |re.S).group(1)
        image =  'https://rominafurniture.com' + image_url_stub
        #.replace() Removes unicode characters
        # description = response.xpath('//div[@class="std"]/p/text()').extract_first().replace(u'\xa0', u' ')
        #The price for the product changes dynamically at the last minute, this price may be off
        original_price = re.search(r'<meta property="og:price:amount"\s*content="([^"]*?)">', response.text, flags=re.I | re.S)

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

        final_price = modifyPriceList(original_price.group(1))
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
        # load_item['description'] = description
        load_item['lowestprice'] = final_price
        #Returns object with each load_item included
        yield load_item
