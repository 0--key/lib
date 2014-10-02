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

class ThePlumbStoreSpider(BaseSpider):
    name = 'theplumbstore.com'
    allowed_domains = ['theplumbstore.com']

    def __init__(self, *args, **kwargs):
        super(ThePlumbStoreSpider, self).__init__(*args, **kwargs)
        csv_file = csv.reader(open(os.path.join(HERE, 'theplumbstore_list.csv')))
        self.products = [(row[0],row[6]) for row in csv_file if row[7].lower()=='yes']


    def start_requests(self):
        for sku, name in self.products:
            n_sku = sku.strip().replace('+','%2B')
            name = name.lower()
            url = 'http://www.theplumbstore.com/catalogsearch/result/?q=' + n_sku
            yield Request(url, meta={'name':name, 'sku': sku})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//li[@class="item first"]')
        for product in products:
            name = products.select('h2[@class="product-name"]/a/text()').extract()[0].lower()
            if name==response.meta['name']:
                loader = ProductLoader(item=Product(), selector=product)   
                loader.add_xpath('name', 'h2[@class="product-name"]/a/text()')
                loader.add_xpath('url', 'h2[@class="product-name"]/a/@href')
                loader.add_xpath('price', 'div[@class="price-box"]/span[@class="price-excluding-tax"]/span[@class="price"]/text()')
                loader.add_value('sku', response.meta['sku'])
                yield loader.load_item()
