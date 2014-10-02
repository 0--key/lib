import re
import os
import logging

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode

import csv

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class VitaminFixSpider(BaseSpider):
    name = 'vitaminfix.com'
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5'

    allowed_domains = ['www.vitaminfix.com', 'vitaminfix.com']
    #start_urls = ('http://www.vitaminfix.com/',)

    def __init__(self, *args, **kwargs):
        super(VitaminFixSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        req = Request('http://www.vitaminfix.com/')
        req.headers['Accept-Language'] = 'en-us,en;q=0.5'
        yield req

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
                    return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//div[@id="mainNav"]//a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            req = Request(url)
            req.headers['Accept-Language'] = 'en-us,en;q=0.5'
            yield req

        # pages
        next_page = hxs.select(u'//a[@class="next i-next"]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            req = Request(next_page)
            req.headers['Accept-Language'] = 'en-us,en;q=0.5'
            yield req

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
            url = product.select(u'.//a[@class="product-data"]/@href').extract()[0]
            url = urljoin_rfc(get_base_url(response), url)
            product_loader.add_value('url', url)
            name = product.select(u'.//a[@class="product-data"]/strong/text()').extract()[0]
            name += ' ' + product.select(u'.//a[@class="product-data"]/span[@class="product-name"]//text()').extract()[0]
            product_loader.add_value('name', name)
            product_loader.add_xpath('price', u'.//span[@class="special-price"]/span/text()',
                                    re=u'\$(.*)')
            product_loader.add_xpath('price', u'.//span[@class="our-price"]/span/text()',
                                    re=u'\$(.*)')
            yield product_loader.load_item()
