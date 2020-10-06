import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

import csv

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class WYeomansSpider(BaseSpider):
    name = 'yeomansoutdoors.co.uk'
    allowed_domains = ['yeomansoutdoors.co.uk']
    #start_urls = ['http://www.yeomansoutdoors.co.uk/']

    def __init__(self, *args, **kwargs):
        super(WYeomansSpider, self).__init__(*args, **kwargs)
        csv_file = csv.reader(open(os.path.join(HERE, 'YeomansURLs.csv')))
        self.products = dict([[row[2], row[0]] for row in csv_file])
     
    def start_requests(self):
        for url in self.products.keys():
            yield Request(url)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        if self.products.has_key(response.url):
            sku = self.products[response.url]
            loader = ProductLoader(item=Product(), response=response)
            loader.add_value('sku', sku)
            loader.add_value('url', response.url)
            loader.add_xpath('name', '//*[@id="feature_content_info"]/h1/text()')
            loader.add_xpath('price', '//*[@id="productBuy"]/p/span/text()')
            return loader.load_item()

