# -*- coding: utf-8 -*-
from scrapy import Spider
from proto_spider.items import productSpiderItem
from scrapy.http import Request
import re

class SmartfurnitureSpider(Spider):
    name = 'smartfurniture'
    custom_settings = {'ELASTICSEARCH_INDEX': 'smartfurniture'}
    allowed_domains = ['smartfurniture.com']
    start_urls = ['https://www.smartfurniture.com/productsearch?w=fsc&isort=score&cnt=120&af=brand:gusmodern+brand:copelandfurniture']

    def parse(self, response):
        products = response.xpath('//div[@class="row product-listing"]//a[@class="product-image-link"]/@href').extract()
        for product in products:
            yield Request(product, callback=self.parse_product, dont_filter=True)
        # Begin processing next page
        # absolute_next_page_url = 'https://smartfurniture.com' + response.xpath('//div[@class="pager"]/a[text()="Next"]/@href').extract_first()
        # yield Request(absolute_next_page_url, callback=self.parse, dont_filter=True)

    def parse_product(self, response):
        productname = response.xpath('//title/text()').extract_first()
        product_url = 'https://smartfurniture.com' + response.xpath('//body/div/@data-url').extract_first()
        #Returns a list, image will be 8th in the list(On zero-based index)
        image = re.search(r'<a\s*href="//([^"]*?)">\s*<div\s*class="square-image', response.text, flags=re.I |re.S)
        description = response.xpath('//meta[@name="description"]/@content').extract_first()
        pricing = re.search(r'<div class="product-price-details\s*"[^>]*?data-sale-price="([^"]*?)"\s*data-original-price="([^"]*?)"', response.text, flags=re.I | re.S)
        lowest_price = pricing.group(1)
        price = pricing.group(2)
        check_greenguard = response.xpath('//*[text()[contains(.,"GREENGUARD")]]')
        check_fsc = response.xpath('//*[text()[contains(.,"FSC")]]')
        #Both FSC and Greenguard products
        def find_certifications():
            cert_container = []
            if check_greenguard and check_fsc:
                cert_container.extend(("GREENGUARD Certified", "Forest Stewardship Council (FSC) Certified"))
            elif check_greenguard:
                cert_container.append('GREENGUARD Certified')
            elif check_fsc:
                cert_container.append('Forest Stewardship Council (FSC) Certified')
            return cert_container

        certifications = find_certifications()

        load_item = productSpiderItem()

        load_item['sitename'] = 'Smart Furniture'
        load_item['productname'] = productname
        load_item['producturl'] = product_url
        load_item['image'] = image.group(1)
        load_item['price'] = price
        load_item['certifications'] = certifications
        load_item['description'] = description
        load_item['lowestprice'] = lowest_price
        #Returns object with each load_item included
        yield load_item
