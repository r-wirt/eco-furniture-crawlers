# -*- coding: utf-8 -*-
from scrapy import Spider
from proto_spider.items import productSpiderItem
from scrapy.http import Request

class StemgoodsSpider(Spider):
    name = 'stem'
    custom_settings = {'ELASTICSEARCH_INDEX': 'stem'}
    allowed_domains = ['stemgoods.com']
    start_urls = ['https://www.stemgoods.com/shop/sofas.html'
                  'https://www.stemgoods.com/shop/sectionals.html',
                  'https://www.stemgoods.com/shop/sleeper-sofas.html',
                  'https://www.stemgoods.com/shop/loveseats.html',
                  'https://www.stemgoods.com/shop/headboards.html',
                  'https://www.stemgoods.com/shop/beds.html',
                  'https://www.stemgoods.com/shop/dressers-armoires.html',
                  'https://www.stemgoods.com/shop/nightstands.html',
                  'https://www.stemgoods.com/shop/credenzas.html',
                  'https://www.stemgoods.com/shop/media-centers.html',
                  'https://www.stemgoods.com/shop/accent-chairs.html',
                  'https://www.stemgoods.com/shop/dining-chairs.html',
                  'https://www.stemgoods.com/shop/benches-ottomans.html'
                  'https://www.stemgoods.com/shop/dining-tables.html',
                  'https://www.stemgoods.com/shop/accent-tables.html',
                  'https://www.stemgoods.com/shop/desks.html']

    def parse(self, response):
        products = response.xpath('//h3[@class="product-name"]/a/@href').extract()
        for product in products:
            yield Request(product, callback=self.parse_product, dont_filter=True)

    def parse_product(self, response):
        #Check the products description section on the page to make sure it is FSC Certified
        check_for_fsc_cert = response.xpath('//div[@class="row multi-column-row"]/div[contains(.,"FSC")]').extract()
        if check_for_fsc_cert == []:
            return

        product_name = response.xpath('//meta[@property="og:title"]/@content').extract_first()
        product_url = response.xpath('//meta[@property="og:url"]/@content').extract_first()
        image = response.xpath('//meta[@property="og:image"]/@content').extract_first()
        description = response.xpath('//meta[@property="og:description"]/@content').extract_first()
        string_of_price = response.xpath('//meta[@property="og:price:amount"]/@content').extract_first()

        def modifyPrice(thePrice):
            price_container = []
            price_without_commas = thePrice.replace(',','')
            price_as_number = float(price_without_commas)
            price_container.append(price_as_number)
            return price_container

        final_price = modifyPrice(string_of_price)
        #Most of the eco-products on WestElm are FSC Certified
        #Currently no Greenguard Products have been noted for this store
        certifications = [{"certification": "Forest Stewardship (FSC) Certified",
                          "title": "FSC Certified products help reduce deforestation by ensuring products have been manufactured with recycled wood materials or have originated from sustainably managed forests.",
                          "url": "https://us.fsc.org/en-us/what-we-do/mission-and-vision"}]
        #Currently no price span for any products on Stem Goods
        lowest_price = final_price[0]

        load_item = productSpiderItem()

        load_item['sitename'] = 'Stem'
        load_item['productname'] = product_name
        load_item['producturl'] = product_url
        load_item['image'] = image
        load_item['price'] = final_price
        load_item['certifications'] = certifications
        load_item['description'] = description
        load_item['lowestprice'] = lowest_price
        #Returns object with each load_item included
        yield load_item
