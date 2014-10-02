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

class TotalBevSpider(BaseSpider):
    name = 'totalbev.com'
    allowed_domains = ['www.totalbev.com', 'totalbev.com']
    start_urls = ('http://www.totalbev.com/Default.aspx?PageID=57', )

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//div[@id="ctl00_ContentPlaceHolder1_shopping"]//a[@class="textlinksmall"]/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pagination
        # next_page = hxs.select(u'').extract()
        # if next_page:
            # next_page = urljoin_rfc(get_base_url(response), next_page[0])
            # yield Request(next_page)

        # products
        for product in self.parse_product(response):
            yield product

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        products = hxs.select(u'//tr[child::td[@valign="top" and child::font[child::b]]]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_value('url', response.url)
            name = product.select(u'./td[position()=3]/font/b/text()').extract()
            if not name:
                name = product.select(u'./td[position()=3]/text()').extract()
            name = name[0].strip()
            bottle_size = product.select(u'./td[position()=4]/font/b/text()').extract()
            if not bottle_size:
                bottle_size = product.select(u'./td[position()=4]/text()').extract()
            if bottle_size:
                name += u' %s' % bottle_size[0].strip()
            price = product.select(u'./td[position()=5]/font/b/text()').extract()[0].strip()
            loader.add_value('name', name)
            loader.add_value('price', price)
            if loader.get_output_value('price'):
                yield loader.load_item()
