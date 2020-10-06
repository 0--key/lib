import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode

import csv

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class DionwiredSpider(BaseSpider):
    name = 'dionwired.co.za'
    allowed_domains = ['dionwired.co.za']
    start_urls = ('http://www.dionwired.co.za/audio-visual.html',
                  'http://www.dionwired.co.za/entertainment.html',
                  'http://www.dionwired.co.za/computing.html',
                  'http://www.dionwired.co.za/appliances.html',
                  'http://www.dionwired.co.za/photographic-optics.html',
                  'http://www.dionwired.co.za/mobile.html')

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        pages = hxs.select('//div[@class="pages"]//a/@href').extract()
        for page in pages:
            yield Request(page)

        for product in self.parse_products(hxs, response):
            yield product

    def parse_products(self, hxs, response):
        products = hxs.select('//ul[@class="products-grid"]//li[starts-with(@class, "item")]')

        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', './/h2[@class="product-name"]/a/text()')
            loader.add_xpath('url', './/h2[@class="product-name"]/a/@href')
            loader.add_xpath('price', './/p[@class="special-price"]//span[@class="price"]/text()')
            loader.add_xpath('price', './/span[@class="price"]/text()')
            loader.add_xpath('sku', './/span[starts-with(text(), "Model: ")]/text()', re='Model: (.*)')

            yield loader.load_item()
