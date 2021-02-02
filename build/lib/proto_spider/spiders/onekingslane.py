# -*- coding: utf-8 -*-
from scrapy import Spider
from proto_spider.items import productSpiderItem
from scrapy.http import Request

#Spider currently allocates all outdoor furniture from the brand International Home Miami
class OnekingslaneSpider(Spider):
    name = 'onekingslane'
    custom_settings = {'ELASTICSEARCH_INDEX': 'onekingslane'}
    allowed_domains = ['onekingslane.com']
    #URL starts at the brand page for Internaional Home Miami furniture
    #It is currently the predominant brand with certified goods on the site
    start_urls = ['https://www.onekingslane.com/c/brands/international-home-miami.do?brand_name=International+Home+Miami&c=101509.104390&sortby=ourPicksAscend&pp=99&page=1']

    def parse(self, response):
        #URL Links to each product within International Home Miami's brand page
        products = response.xpath('//div[@class="ml-thumb-name"]/a/@href').extract()
        for product in products:
            yield Request('https://www.onekingslane.com' + product, callback=self.parse_product, dont_filter=True)
        #Begin processing next page
        #absolute_next_page_url = 'https://www.onekingslane.com' + response.xpath('//ul[@class="pagination"]//li[@class=" ml-paging-default"]/a/@href').extract_first()
        #yield Request(absolute_next_page_url, callback=self.parse, dont_filter=True)

    def parse_product(self, response):
        #Check the products description section on the page to make sure it is FSC Certified
        check_for_fsc_cert = response.xpath('//p[text()[contains(.,"FSC")]]').extract()
        if check_for_fsc_cert == []:
            return
        product_name = response.xpath('//div[@class="ml-product-name"]/div/text()').extract_first()
        product_url = response.xpath('//link[@rel="alternate"]/@href').extract_first()
        image = response.xpath('//div[@class="ml-product-alt-detail-image"]//img/@src').extract_first()
        #Some product pages render the product images dynamically, after scrapy has rendered page
        #This following if-statement is used to move on to next product if image was not rendered in page
        if image == None:
            return

        description = response.xpath('//meta[@name="description"]/@content').extract_first()
        original_price = response.xpath('//span[@class="ml-item-price"]/text()').extract_first()

        #The prices will be returned as a string, and they may also have commas and '$' in them,
        #This function is intended to remove any commas and '$' then turn the strings into integers
        def modifyPriceList (thePrice):
            price_container = []
            #Takes dollar sign and commas out of price
            price_without_commas = thePrice.replace(',','').replace('$','')
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

        load_item['sitename'] = 'One Kings Lane'
        load_item['productname'] = product_name
        load_item['producturl'] = product_url
        load_item['image'] = image
        load_item['price'] = final_price
        load_item['certifications'] = certifications
        load_item['description'] = description
        load_item['lowestprice'] = final_price[0]
        #Returns object with each load_item included
        yield load_item
