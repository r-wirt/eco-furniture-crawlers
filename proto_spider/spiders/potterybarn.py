# -*- coding: utf-8 -*-
from scrapy import Spider
from proto_spider.items import productSpiderItem
from scrapy.http import Request
import ast
import json

#Most FSC Certified furniture on PotteryBarn is currently outdoor furniture,
#The following scraper yields outdoor furniture products only
class PotterybarnSpider(Spider):
    name = 'potterybarn'
    custom_settings = {'ELASTICSEARCH_INDEX': 'potterybarn'}
    allowed_domains = ['potterybarn.com']
    start_urls = ['https://core.dxpapi.com/api/v1/core/?q=fsc-wood-outdoor-furniture&start=0&rows=20&request_type=search&search_type=category&request_id=277390464&_br_uid_2=uid=2353288239327:v=12.0:ts=1610679940296:hc=21&account_id=4068&url=https://www.potterybarn.com/&domain_key=potterybarn_en_pb_prd_d1&fq=inactive:"false"&fq=availability_logic:"true"&fl=pid,price,price_range,sale_price,sale_price_range,thumb_image,title,eligibleForQuickBuy,pipThumbnailMessages,flags,skuid,sku_price,sku_sale_price,swatch_image_for_sku,thumb_image_for_sku,isBopisOnly,priceType,imageOverride,altImages,store_ids,category_name_attr,category_id_attr,swatchOrder,pageLoadImages,imageRollOvers,hoverImages,swatchLabel,thumb_image_attr,leaderSkuImage&efq=ship_to_store_ids:("ST:6238") OR store_ids:("ST:6238") OR fulfillment_locations:("CMH_CMO" OR "CDCDTC" OR "CMH_SS" OR "DEFAULT")']
    #CHECK THE FOLLOWING for start_url ----> Make sure includes outdoor products
    #https://www.potterybarn.com/shop/outdoor/fsc-wood-outdoor-furniture/?cm_type=gnav

    def parse(self, response):
        #*****Scipting for infinite scroll currently not required*****

        #self.driver.get(response.request.url)
        #Scroll down to the end of page to initiate infinite scroll
        #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #Wait for newly scrolled results to arrive on page
        #time.sleep(15)
        #res = response.replace(body=self.driver.page_source)

        json_data = json.loads(response.text)


        products = json_data['response']['docs']

        headers = {
        'host': 'www.potterybarn.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        # 'cookie': 'TnTNew=true; WSPFY=df60dc17447500007506016040000000f5a80000; s_ecid=MCMID%7C56492272042462241730500808037603111691; crl8.fpcuid=bd214f89-eb9d-4e1a-a557-b5579179393a; _abck=45FE5D686EC23173B931A378DE1CA07F~0~YAAQ32DcF+KmhfZ2AQAAo1wBBAXsxgrcwi8jP6C8hLS7mONiqK1OwE26qWe0lFtkH1xVBffaBIonbKbPRYfhbT1Ycu8cYQbsQ1Kl2KK1DwbVnIWEW7o+KeGAtWd4zzCW4vd1KH1xqmoODKva0zK2E0VNSpyllzg420MLWknTrZbBJkSFDVi0gpasjz4rAPaq3AWSgN35tfmGVV6oxuIF6tOc+842MJMrHm5rJNhCjhIyOyKuZ5ZK35lfcq1O47ONLjmGW8JCJeBWUq/VYzwYrf4AcLIgDszss/OUmF1F0k2Zn1cShfDeQVsXQ1mZF27UbZ9V83Sh6TjoOtHBT9SCPgotan3CLMmLa53p~-1~||-1||~-1; svi_dec=56492272042462241730500808037603111691; _gcl_au=1.1.1587875309.1610679940; _svsid=ecdd42154fb81382664e20905c3e3ebe; _pin_unauth=dWlkPVpXVmtPR0l3TW1NdE1HSmpNQzAwTldObUxUazJOVGt0TXpka01EQXpNV0psWWpVMA; fpcid=2731891553318865260_FP; _ga=GA1.2.730799650.1610679943; tracker_device=1d454c75-1c4c-416f-9c81-8a9a5e4ad614; stickyOverlayMinimized=1; _fbp=fb.1.1610679953621.316097334; zipCodeAvailability=44101%7Ctrue%7CEast%20Primary%7Cfalse%7Cfalse; TURNTO_TEASER_COOKIE=a,1610680175238; bm_sz=A310FD9314D2E5E74FB72FBAF98689CA~YAAQlmDcF/s+NSd3AQAAYcJXNwqpoj28ao5u4p90by/1kFL+YH0FfV6ST/4iHHQk2ECa28/Gp5KIRWysu91QXdowRU7rCM04FQae6r4Euo21sjPKbg34vuFV2fct6Xsp4D+Jd7c6LHjsOHoRz8Lk7Whuvm3IrCfs9NrHwIEsKOFixBT7Y9z9RrNQ50L/KXPcTPghaNY=; ak_bmsc=72480A669E39DE40869D1BB0089BA2B517DC6096074C0000F22A0E60D3D6095F~plTa+OBm2hir08EF/8a/hT3lmRD60fTrGL1E+aBDtmckPsMbr5F5CU/Vo0myZeavXM2+WtOavcqvxOrx8LE5rYtzsl5IAsYEepad2wUdv9k+JjIvb03Des9sU6gymuiIzNFsYIoMiJVG+4DTiHntsUD+M0RWA2rdSAC8hICr0UrPNhJh6n54Y0xsM9o2ycuPvNj7LaJNKac2Xdi5N8aIhgyn4HearkUfV59iLDP18YEsk=; check=true; AMCVS_D38758195432E1050A4C98A2%40AdobeOrg=1; AMCV_D38758195432E1050A4C98A2%40AdobeOrg=1075005958%7CMCIDTS%7C18653%7CMCMID%7C56492272042462241730500808037603111691%7CMCAAMLH-1612146036%7C7%7CMCAAMB-1612146036%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1611548436s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.4.1%7CMCCIDH%7C2128427398; WSIDC=EAST; INTERNATIONAL=US-USD-1; ad_sess_pb_email=true; s_fid=4EB34AF94E83F60B-14D2D1D7D72898DD; IR_gbd=potterybarn.com; s_cc=true; jl_usrid.5c7d559730e4b979fb48cdf9.pottery_barn=jluuid_e0d372f0-601e-4f40-a10c-527b2f90948b; kenshoo_id_match=b334b989-8395-1975-19d4-8240ece35ab0; kenshoo_tapad_id_sync=f0dfa459-d9d4-3227-a48f-98aee9374675; _gid=GA1.2.963627086.1611541243; mboxEdgeCluster=34; wsiakid=0FMnCN7aEZvSJHwVLsDcl2IjXoLc7QB5ZvIXtamNQQuurfuIn8lPseLt66r0taggIWtF/8G7uWtL1PwnAxmuo2EOsSsmJVonVGN306se8EM=; akid=36yVbX_ufbwD_e2t8fLg63IX2Fx56c9xltsWu3XAe-oN-M-g1jb8nmQ; PBRN=3QUQFMWVUMlfDDvOJ_fyzF44r0zY7bEi24Q3OKmwpjjolyu-72wWwhw; s_lv_s=Less%20than%201%20day; TT3bl=false; TURNTO_VISITOR_SESSION=1; TURNTO_VISITOR_COOKIE=eIgv3axq2p5JMQf,1,0,0,null,,,0,0,0,0,0,0,0; PBPE_SID=pb35prdabJMFQZ6YV84CQEFQHS2XISS4202101241857; PBPE_SSID=dWFOKriA4AL34KHDLO2L9QWH0IG0LOLIXI1B6E1K; s_vst1=1; CreState=H1pi52aetTUYNvqDvEjRv08pptxsbxKiv%2BCvNI718ohZy05ob3VPAKGP41uhQH%2B5f7H7sME2EFTJPRsq0TkLMw%3D%3D.195.v1; productnum=21; WSGEO=US|OH|44101|41.4995|-81.6959; TURNTO_TEASER_SHOWN=1611544836982; mbox=PC#a63f40af9ae04a879243003fc1ad4a5f.34_0#1674786306|session#24e6774989fa422e8d2c0e614e400f8a#1611546698; bm_sv=AEE852917CEA0FEC42450B90D340C2EB~uTa1klXHVTQlPrcwf9evbmNdJg5ollYOtarxcamgCofXBh8dL50aUqIxin3fWOIfpHJGkjLXkq33g7NWcKylpQ4hrn2+QDFV3IsbwHNADxj/jb9crzVkP0J2tb/4ESDzVaR4EriKvPaSyhehVvbMZAafIZcc7TSovsFYGHsOvM4=; BIGipServerPool-PB-49446=!f8DrMhUCT+C7aEpBy/3bykxFFdl+Kvw6z+aIfEv5RKvy2185sCFtuy2R0/GQ/zM7Re3kRO7Kz7MW; pageLoadTime=4662; gpv_p46=no%20value; gpv_p19=product%20detail%3Abelgian-flax-linen-diamond-quilt-white; s_lv=1611544840480; s_nr44=1611544840485-Repeat; s_sq=wsiwsdev%3D%2526c.%2526a.%2526activitymap.%2526page%253Dhttps%25253A%25252F%25252Fwww.potterybarn.com%25252Fshop%25252Foutdoor%25252Ffsc-wood-outdoor-furniture%25252F%25253Fisx%25253D0.0.0%2526link%253DMinimize%2526region%253Djoin-email-campaign%2526.activitymap%2526.a%2526.c; rr_rcs=eF4NyLERgDAIBdAmlbv8nBDAsIFzEOKdhZ06v77yleV67zMrcwcZkYr05u4MWQEqz9jFpg_nA63p3xkJ7aGgqblxaBrbB2T1EWg; _br_uid_2=uid%3D2353288239327%3Av%3D12.0%3Ats%3D1610679940296%3Ahc%3D36; IR_4332=1611544841330%7C0%7C1611543479288%7C%7C; IR_PI=8c975b63-56de-11eb-bba4-02caec40f184%7C1611631241330; _uetsid=eac393205eb311eb989c51dbd3f81c76; _uetvid=8c4202b056de11ebb823bb2fe99ece87; utag_main=v_id:0177040161b300610f3d7bd8aa8403078001c07000918$_sn:3$_ss:0$_st:1611546642052$vapi_domain:potterybarn.com$_prevpage:product%20detail%3Abelgian-flax-linen-diamond-quilt-white%3Bexp-1611548440223$_pn:10%3Bexp-session$ses_id:1611543477352%3Bexp-session$prev_page_primary_category:product%20detail%3Acomplex%20pip%3Bexp-session; _derived_epik=dj0yJnU9R3ctS2pROGg4NGhBdGJISmtDSlJBTXg1RUZQTmhpMlEmbj04N09Ub3JzaGw2UXQ2VTVPZklfTV9BJm09MSZ0PUFBQUFBR0FPT1FrJnJtPTEmcnQ9QUFBQUFHQU9PUWs; _gat_gtag_UA_108284962_1=1; s_tp=8133; s_ppv=product%2520detail%253Abelgian-flax-linen-diamond-quilt-white%2C12%2C12%2C945; RT="z=1&dm=potterybarn.com&si=72276716-9d81-4879-9c11-6c48a1fcb2de&ss=kkby1hyt&sl=e&se=2s0&tt=1ikd&bcn=%2F%2Fb855d71c.akstat.io%2F&ld=259n4&ul=2601t"',
        # 'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        # 'sec-ch-ua-mobile': '?0',
        # 'sec-fetch-dest': 'document',
        # 'sec-fetch-mode': 'navigate',
        # 'sec-fetch-site': 'same-origin',
        # 'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'
        }
        for product in products:
            product_id = product['pid']
            product_url = 'https://www.potterybarn.com/products/' + product_id
            yield Request(product_url, headers=headers, callback=self.parse_product, dont_filter=True)

    def parse_product(self, response):
        product_name = "Outdoor: " + response.xpath('//head/meta[@property="og:title"]/@content').extract_first()
        #Remove registered trade mark from string since it arrives as numeric
        #representation of the non-ascii character
        product_name = product_name.replace("&#0174;", "")
        print(product_name)

        product_url = response.xpath('//head/meta[@property="og:url"]/@content').extract_first()
        image = response.xpath('//head/meta[@property="og:image"]/@content').extract_first()
        #Description response will have unicode characters in scrapy shell but they are parsed into utf-8
        #when it is sent via ElasticSearch pipeline
        description = response.xpath('//head/meta[@property="twitter:description"]/@content').extract_first()
        #The following line will return the price(s) as a string in a list, and it may also have commas.
        original_price_span = response.xpath('//section[@class="simple-subset"]//span[@class="price-amount"]/text()').extract()

        #Some Pottery Barn products list a price range for different sizes
        #Products with a price range must be grabbed from a different section on product page
        #This function is intended to remove any commas and turn the strings into integers
        #The function also grabs the low and high price if original_price_span is empty
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
        #Most of the eco-products on 2modern are FSC Certified
        #Currently no Greenguard Products have been noted for this store
        certifications = [{"certification": "Forest Stewardship (FSC) Certified",
                          "title": "FSC Certified products help reduce deforestation by ensuring products have been manufactured with recycled wood materials or have originated from sustainably managed forests.",
                          "url": "https://us.fsc.org/en-us/what-we-do/mission-and-vision"}]
        #In order for elasticsearch to sort the products by price amount it will need the first
        #one in the array if there is a price range for the product
        lowest_price = final_price_span[0]

        load_item = productSpiderItem()

        load_item['sitename'] = 'Pottery Barn'
        load_item['productname'] = product_name
        load_item['producturl'] = product_url
        load_item['image'] = image
        load_item['price'] = final_price_span
        load_item['certifications'] = certifications
        load_item['description'] = description
        load_item['lowestprice'] = lowest_price
        #Returns object with each load_item included
        yield load_item
