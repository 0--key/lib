import os
import csv
import string
from scrapy import log
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url
from product_spiders.fuzzywuzzy import process

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class ValueBasketSpider(BaseSpider):
    name = 'valuebasket.com'
    allowed_domains = ['valuebasket.com']
    start_urls = ['http://www.valuebasket.com/en_GB']

    def parse(self, response):
        cookies = {'custom_country_id': 'GB'}
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//*[@id="sub-navigation"]/div/ul/li/p/a/@href').extract()
        for category in categories:
            url = urljoin_rfc(get_base_url(response), category)
            yield Request(url, callback=self.parse_products, cookies=cookies)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//ul[@class="products border-radius-3 grid-view"]/li')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', 'div/h4/a/text()')
            loader.add_xpath('url', 'div/h4/a/@href')
            loader.add_xpath('price', 'div/ins/strong/text()')
            yield loader.load_item()
        next = hxs.select('//li[@class="next"]/a/@href').extract()
        if next:
            url = urljoin_rfc(get_base_url(response), next[0])
            yield Request(url, callback=self.parse_products)
