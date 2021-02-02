# -*- coding: utf-8 -*-
from scrapy import Spider
from selenium import webdriver
from proto_spider.items import productSpiderItem
from scrapy.http import Request
import ast

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-setuid-sandbox')


class westElmSpider(Spider):
    name = 'westelm'
    custom_settings = { 'ELASTICSEARCH_INDEX': 'westelm' }
    allowed_domains = ['westelm.com']
    #Scrape search while page is in 'view all' setting
    start_urls = ['https://www.westelm.com/search/results.html?N=&cm_sp=HeaderLinks-_-OnsiteSearch-_-MainSite&cm_type=OnsiteSearch&itemsPerPage=24&page=viewall&sortBy=best&words=fsc']

    def __init__(self):
        global chrome_options
        self.driver = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=chrome_options)


    def parse(self, response):
        self.driver.get(response.request.url)
        res = response.replace(body=self.driver.page_source)
        #URL Links to each product within 'FSC' results
        #Spider currently voids build-your-own furniture
        products = res.xpath("//div[@class='toolbox-for-product-cell']/a/@href").extract()
        for product in products:
            yield Request(product, callback=self.parse_product, dont_filter=True)

        #Begin processing next page
        #absolute_next_page_url = res.xpath("//li[@class='next-page']/a/@href").extract_first()
        #yield Request(absolute_next_page_url, callback=self.parse, dont_filter=True)

    def parse_product(self, response):

        productname = response.xpath('//div[@class="pip-summary"]/h1/text()').extract_first()
        product_url = response.xpath('//head/meta[@property="og:url"]/@content').extract_first()
        image = response.xpath('//head/meta[@property="og:image"]/@content').extract_first()
        description = response.xpath('//head/meta[@property="twitter:description"]/@content').extract_first()

        #The following line will return the price(s) as a string, and it may also have commas.
        original_price_span = response.xpath('//section[@class="simple-subset"]//span[@class="price-amount"]/text()').extract()

        #Some West Elm products list a price range for different sizes
        #Products with a price range must be grabbed from a different section on the product page
        #This function is intended to remove any commas and turn the strings into integers
        #The function also grabs the low and high price if original_price_span is empty for some reason
        def modifyPriceList (thePriceSpan):

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

        final_price_span = modifyPriceList(original_price_span)
        #Most of the eco-products on WestElm are FSC Certified
        #Currently no Greenguard Products have been noted for this store
        certifications = [{"certification": "Forest Stewardship (FSC) Certified",
                          "title": "FSC Certified products help reduce deforestation by ensuring products have been manufactured with recycled wood materials or have originated from sustainably managed forests.",
                          "url": "https://us.fsc.org/en-us/what-we-do/mission-and-vision"}]
        #In order for elasticsearch to sort the products by price amount it will need the first
        #one in the array if there is a price range for the product
        lowest_price = final_price_span[0]

        load_item = productSpiderItem()

        load_item['sitename'] = 'west elm'
        load_item['productname'] = productname
        load_item['producturl'] = product_url
        load_item['image'] = image
        load_item['price'] = final_price_span
        load_item['certifications'] = certifications
        load_item['description'] = description
        load_item['lowestprice'] = lowest_price
        #Returns object with each load_item included
        yield load_item
