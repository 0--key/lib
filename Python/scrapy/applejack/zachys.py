import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode
import hashlib

import csv

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))

class ZachysSpider(BaseSpider):
    name = 'zachys.com'
    allowed_domains = ['www.zachys.com', 'zachys.com']
    start_urls = ('http://www.zachys.com/retail/Default.aspx?Ne=26&N=0&Nr=64', )

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        prices = hxs.select(u'//span[@class="e_nav_item" and contains(text(),"Price")]/../../following-sibling::div[1]//a/@href').extract()
        for url in prices:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pagination
        next_page = hxs.select(u'//a[@title="Next Page"]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(next_page)

        # products
        for product in self.parse_product(response):
            yield product

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        products = hxs.select(u'//dl[@class="search_result"]')
        for product in products:
            url = product.select(u'./dt/a[@class="#"]/@href').extract()[0]
            url = urljoin_rfc(get_base_url(response), url)
            multiple_prices = product.select(u'.//dd[@class="prices"]')
            name = product.select(u'./dt/a[@class="#"]/text()').extract()[0].strip() + u' %s'
            for option in multiple_prices:
                price_xpath = u'.//td[%s]/following-sibling::td[1]/text()'
                if option.select(u'.//td[@class="sale"]'):
                    price_xpath %= u'@class="sale" and %s'
                price_xpath %= u'contains(text(),"%s")'
                product_types = [u'Item', u'Bottle', u'Case']
                for product_type in product_types:
                    loader = ProductLoader(item=Product(), selector=product)
                    loader.add_value('url', url)
                    price = option.select(price_xpath % product_type)
                    if price:
                        loader.add_value('name', name % product_type)
                        loader.add_value('price', price.extract())
                        yield loader.load_item()
