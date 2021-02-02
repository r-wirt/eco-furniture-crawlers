# -*- coding: utf-8 -*-
from scrapy import Spider
from selenium import webdriver
from proto_spider.items import productSpiderItem
from scrapy.http import Request

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-setuid-sandbox')


class Apt2bSpider(Spider):
    name = 'apt2b'
    custom_settings = {'ELASTICSEARCH_INDEX': 'apt2b'}
    allowed_domains = ['apt2b.com']
    #Each start_url represents an aggregated category, this is currently best to avert site's infinite scroll
    start_urls = ['https://www.apt2b.com/pages/search-results?q=fsc&narrow=%5B%5B%22Type%22%2C%22Sofas%22%5D%5D&disable_semantics=1',
                  'https://www.apt2b.com/pages/search-results?q=fsc&narrow=%5B%5B%22Type%22%2C%22Accent%20Chair%22%5D%5D&disable_semantics=1',
                  'https://www.apt2b.com/pages/search-results?q=fsc&narrow=%5B%5B%22Type%22%2C%22Modular%22%5D%5D&disable_semantics=1',
                  'https://www.apt2b.com/pages/search-results?q=fsc&narrow=%5B%5B%22Type%22%2C%22Apartment%20Size%20Sofa%22%5D%5D&disable_semantics=1',
                  'https://www.apt2b.com/pages/search-results?q=fsc&narrow=%5B%5B%22Type%22%2C%22Sectional%22%5D%5D&disable_semantics=1',
                  'https://www.apt2b.com/pages/search-results?q=fsc&narrow=%5B%5B%22Type%22%2C%22Dining%20Table%22%5D%5D&disable_semantics=1',
                  'https://www.apt2b.com/pages/search-results?q=fsc&narrow=%5B%5B%22Type%22%2C%22Bed%22%5D%5D&disable_semantics=1',
                  'https://www.apt2b.com/pages/search-results?q=fsc&narrow=%5B%5B%22Type%22%2C%22Chest%22%5D%5D&disable_semantics=1',
                  'https://www.apt2b.com/pages/search-results?q=fsc&narrow=%5B%5B%22Type%22%2C%22Nightstand%22%5D%5D&disable_semantics=1',
                  'https://www.apt2b.com/pages/search-results?q=fsc&narrow=%5B%5B%22Type%22%2C%22CLEARANCE%22%5D%5D&disable_semantics=1']



    def __init__(self):
        global chrome_options
        self.driver = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=chrome_options)

    def parse(self, response):
        self.driver.get(response.request.url)
        #Update response to include additional products from the scroll-down
        res = response.replace(body=self.driver.page_source)
        products = res.xpath('//div/@data-product-url').extract()
        for product in products:
            yield Request(product, callback=self.parse_product,dont_filter=True)

    def parse_product(self, response):
        product_name = response.xpath('//meta[@property="og:title"]/@content').extract_first()
        product_url = response.xpath('//meta[@property="og:url"]/@content').extract_first()
        image = response.xpath('//meta[@property="og:image"]/@content').extract_first()
        description = response.xpath('//meta[@property="og:description"]/@content').extract_first()
        #The following line will return the price(s) as a string inside of a list, and it may also have commas.
        original_price_span = response.xpath('//meta[@property="og:price:amount"]/@content').extract()

        def modifyPriceList(thePriceList):
            price_container = []
            #Takes commas out of price
            for price in thePriceList:
                price_without_commas = price.replace(',','')
                price_container.append(price_without_commas)
            #Convert string in list to floating number
            price_container = list(map(float, price_container))
            return price_container

        final_price_span = modifyPriceList(original_price_span)
        #Most of the eco-products on 2modern are FSC Certified
        #Currently no Greenguard Products have been noted for this store
        certifications = [{"certification": "Forest Stewardship (FSC) Certified",
                          "title": "FSC Certified products help reduce deforestation by ensuring products have been manufactured with recycled wood materials or have originated from sustainably managed forests.",
                          "url": "https://us.fsc.org/en-us/what-we-do/mission-and-vision"}]
        #In order for elasticsearch to sort the products by price amount it will need the first
        #one in the array if there is a price range for the product
        lowest_price = final_price_span[0]

        load_item = productSpiderItem()

        load_item['sitename'] = 'Apt2B'
        load_item['productname'] = product_name
        load_item['producturl'] = product_url
        load_item['image'] = image
        load_item['price'] = final_price_span
        load_item['certifications'] = certifications
        load_item['description'] = description
        load_item['lowestprice'] = lowest_price
        #Returns object with each load_item included
        yield load_item
