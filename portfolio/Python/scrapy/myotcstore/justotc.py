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

class JustOTCSpider(BaseSpider):
    name = 'justotc.com'
    allowed_domains = ['www.justotc.com', 'justotc.com']
    start_urls = ('http://www.justotc.com/brand.html',)

    def __init__(self, *args, **kwargs):
        super(JustOTCSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
                    return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//ul[@class="brand-list"]//a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pages
        next_pages = hxs.select(u'//div[@class="paging" and not(@style)]//a/@href').extract()
        for page in next_pages:
            page = urljoin_rfc(get_base_url(response), page)
            yield Request(page)

        # products
        for product in self.parse_product(response):
            yield product
    
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)
        products = hxs.select(u'//div[@class="product-listing-2"]/div[contains(@class,"rec")]')

        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            url = product.select(u'.//div[@class="description"]/h2/a/@href').extract()[0]
            url = urljoin_rfc(get_base_url(response), url)
            product_loader.add_value('url', url)
            product_loader.add_xpath('name', u'.//div[@class="description"]/h2/a/text()')
            product_loader.add_xpath('price', u'.//span[@class="prod-price"]/text()',
                                 re=u'\$(.*)')
            yield product_loader.load_item()