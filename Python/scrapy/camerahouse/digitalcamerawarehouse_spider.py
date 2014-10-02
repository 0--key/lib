import csv
import os
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.fuzzywuzzy import process
from product_spiders.fuzzywuzzy import fuzz

HERE = os.path.abspath(os.path.dirname(__file__))

class DigitalCameraWarehouseSpider(BaseSpider):
    name = 'digitalcamerawarehouse.com.au'
    allowed_domains = ['digitalcamerawarehouse.com.au']
    start_urls = ['http://www.digitalcamerawarehouse.com.au/']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//table[@id="table1"]/tr/td/font/a/@href').extract()
        for category in categories:
            url =  urljoin_rfc(get_base_url(response), category)
            yield Request(url, self.parse_products)

    def parse_categories(self, response):
        hxs = HtmlXPathSelector(response)
        
        html = hxs.extract().replace('Sub Categories', '<div id="sub_categories">').replace('<p> </p>', '</div>')
        new_hxs = HtmlXPathSelector(text=html)
        sub_categories = new_hxs.select('//*[@id="sub_categories"]/a/@href').extract()
        for sub_category in sub_categories:
            url =  urljoin_rfc(get_base_url(response), sub_category)
            yield Request(url, self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//td[@class="td"]/div[@style="width:750px;'
                              ' padding: 10px 0px 10px 20px; "]/'
                              'table [@width="80%" and @cellpadding="4" and'
                              ' @border="0" and @align="center"]')
        if products:
            for product in products:
                loader = ProductLoader(item=Product(), selector=product)
                loader.add_xpath('name', 'tr/td/table/tr/td/strong/a/text()')
                loader.add_xpath('name', 'tr/td/div/strong/a/text()')
                url = product.select('tr/td/table/tr/td/strong/a/@href').extract()
                if url:
                    url = urljoin_rfc(get_base_url(response), url[0])
                else:
                    url = product.select('tr/td/div/strong/a/@href').extract()
                    if url:
                        url = urljoin_rfc(get_base_url(response), url[0])
                loader.add_value('url', url)
                loader.add_xpath('price', 'tr/td/div[@class="HeadingText"]/text()')
                yield loader.load_item()
        else:
           try: 
               categories = hxs.select('//td[@class="td"]/div[@style="width:750px;'
                                    ' padding: 10px 0px 10px 20px; "]/'
                                    'table[@cellpadding="5"]')
               if categories:
                   for category in categories:
                       url = urljoin_rfc(get_base_url(response), 
                                         category.select('tr/td/a[@class="HeadingText"]/@href').extract()[0])
                       yield Request(url, dont_filter=True, callback=self.parse_products)
           except IndexError:
               pass
        html = hxs.extract().replace('Sub Categories', '<div id="sub_categories">').replace('<p> </p>', '</div>')
        new_hxs = HtmlXPathSelector(text=html)
        sub_categories = new_hxs.select('//*[@id="sub_categories"]/a/@href').extract()
        for sub_category in sub_categories:
            url =  urljoin_rfc(get_base_url(response), sub_category)
            yield Request(url, dont_filter=True, callback=self.parse_products)
        
             
    
        
