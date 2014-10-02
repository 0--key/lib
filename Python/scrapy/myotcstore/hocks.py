import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode

import csv

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class HocksSpider(BaseSpider):
    name = 'hocks.com'
    user_agent = 'Googlebot'
    allowed_domains = ['www.hocks.com', 'hocks.com']
    start_urls = ('http://hocks.com/',)

    def __init__(self, *args, **kwargs):
        super(HocksSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
                    return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//ul[@id="nav"]/li/a[child::span]/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pages
        next_page = hxs.select(u'//a[@class="next i-next"]/@href').extract()
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
        products = hxs.select(u'//li[contains(@class,"item")]')

        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            url = product.select(u'.//h2[@class="product-name"]/a/@href').extract()[0]
            url = urljoin_rfc(get_base_url(response), url)
            product_loader.add_value('url', url)
            product_loader.add_xpath('name', u'.//h2[@class="product-name"]/a/text()')
            product_loader.add_xpath('price', u'.//span[@class="regular-price"]/span[@class="price"]/text()',
                                 re=u'\$(.*)')
            yield product_loader.load_item()