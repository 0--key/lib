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

class KLWinesSpider(BaseSpider):
    name = 'klwines.com'
    allowed_domains = ['www.klwines.com', 'klwines.com']
    start_urls = ('http://www.klwines.com/content.asp?N=0&display=500&Nr=OR%28OutofStock%3AN%2CInventory+Location%3ASpecial+Order%29&Ns=p_lotGeneratedFromPOYN|0||p_price', )

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        # categories = hxs.select(u'').extract()
        # for url in categories:
            # url = urljoin_rfc(get_base_url(response), url)
            # yield Request(url)

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

        products = hxs.select(u'//div[@class="result clearfix"]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            url = product.select(u'.//div[@class="result-desc"]/a/@href').extract()
            name = product.select(u'.//div[@class="result-desc"]/a/text()').extract()
            if not url:
                url = product.select(u'.//div[@class="auctionResult-desc"]/p/a/@href').extract()
                name = product.select(u'.//div[@class="auctionResult-desc"]/p/a/text()').extract()
            url = urljoin_rfc(get_base_url(response), url[0])
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_xpath('price', u'.//span[@class="price"]/span[@class="global-serif global-pop-color"]/strong/text()')
            if loader.get_output_value('price'):
                yield loader.load_item()
