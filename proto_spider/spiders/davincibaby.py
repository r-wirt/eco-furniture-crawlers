# -*- coding: utf-8 -*-
from scrapy import Spider
from proto_spider.items import productSpiderItem
from scrapy.http import Request

#Spider currently allocates all baby cribs from website
class DavincibabySpider(Spider):
    name = 'davincibaby'
    custom_settings = {'ELASTICSEARCH_INDEX': 'davincibaby'}
    allowed_domains = ['davincibaby.com']
    start_urls = ['https://davincibaby.com/collections/cribs']

    def parse(self, response):
        products = response.xpath('//a[@class="grid-view-item__link"]/@href').extract()
        for product in products:
            yield Request('http://www.davincibaby.com' + product, callback= self.parse_product, dont_filter=True)
        #Begin processing next pages
        absolute_next_page_url = response.xpath('//div[@class="pagination row row--5 cf"]//div[@class="item"]/ul//li[last()-1]/a/@href').extract_first()
        yield Request(absolute_next_page_url, callback=self.parse,dont_filter=True)

    def parse_product(self, response):
        #Check the products description section on the page to make sure it is Greenguard Certified
        check_for_gg_cert = response.xpath('//div[@itemprop="description"]//ul').extract_first()
        if 'GREENGUARD' not in check_for_gg_cert:
            return
        product_name = response.xpath('//meta[@property="og:title"]/@content').extract_first()
        product_url = response.xpath('//meta[@property="og:url"]/@content').extract_first()
        image = response.xpath('//meta[@property="og:image"]/@content').extract_first()
        description = response.xpath('//meta[@property="og:description"]/@content').extract_first()
        original_price = response.xpath('//meta[@property="og:price:amount"]/@content').extract_first()

        #The prices will be returned as a string
        #This function is intended to turn the original_price string into an integer
        def modifyPriceList (thePrice):
            price_container = []
            #Turns price_without_commas into floating integer
            price_as_integer = float(thePrice)
            price_container.append(price_as_integer)
            return price_container

        final_price = modifyPriceList(original_price)

        #Most of the eco-products on davincibaby are GREENGUARD Gold Certified
        certifications = [{
"certification": "GREENGUARD Certified",
"title": "GREENGUARD Certified products contain materials and finishes that have been verified to have low chemical emissions. \
 As a result, this product improves overall indoor air quality by reducing the presence of harmful \
 pollutants and airborne chemicals.", "url": "http://greenguard.org/en/CertificationPrograms/CertificationPrograms_indoorAirQuality.aspx"
}]

        load_item = productSpiderItem()

        load_item['sitename'] = 'Davinci Baby'
        load_item['productname'] = product_name
        load_item['producturl'] = product_url
        load_item['image'] = image
        load_item['price'] = final_price
        load_item['certifications'] = certifications
        load_item['description'] = description
        load_item['lowestprice'] = final_price[0]
        #Returns object with each load_item included
        yield load_item
