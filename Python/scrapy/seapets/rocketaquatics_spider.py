import csv
import os
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.fuzzywuzzy import process
from product_spiders.fuzzywuzzy import fuzz

HERE = os.path.abspath(os.path.dirname(__file__))

class RocketAquaticsSpider(BaseSpider):
    name = 'rocketaquatics.co.uk'
    allowed_domains = ['rocketaquatics.co.uk']
    start_urls = ['http://www.rocketaquatics.co.uk']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//table[@class="infoBoxContents"]/tr/td[@class="boxText"]/a/@href').extract()
        for category in categories:
            yield Request(category, callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//tr[@class="productListing-odd" or @class="productListing-even"]')
        if products:
            for product in products:
                loader = ProductLoader(item=Product(), selector=product)   
                loader.add_xpath('name', 'td[not(@align)]/a/text()')
                loader.add_xpath('url', 'td[not(@align)]/a/@href')
                loader.add_xpath('price', 'td[@align="right"]/text()')
                yield loader.load_item()
            next = hxs.select('//a[@class="pageResults" and @title=" Next Page "]/@href').extract()
            if next:
                yield Request(next[0], callback=self.parse_products)
        else:
            sub_categories = hxs.select('//td[@class="tableHeading"]/a/@href').extract()
            for sub_category in sub_categories:
                yield Request(sub_category, callback=self.parse_products)
        
