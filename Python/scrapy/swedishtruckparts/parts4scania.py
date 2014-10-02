import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

import csv

from product_spiders.items import Product, ProductLoader


class Parts4ScaniaSpider(BaseSpider):
    name = 'parts4scania.co.uk'
    allowed_domains = ['www.parts4scania.co.uk']
    start_urls = ('http://www.parts4scania.co.uk',)

    def __init__(self, *args, **kwargs):
        super(Parts4ScaniaSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select('//table[@id="NavigationBar4"]//a/@href').extract()
        for category in categories:
            url = urljoin_rfc(get_base_url(response), category)
            yield Request(url)

        # pages
        # next_page = hxs.select('').extract()
        # if next_page:
        #     url = urljoin_rfc(get_base_url(response), next_page[0])
        #     yield Request(url)

        # products
        for product in self.parse_product(response):
            yield product


    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        # products
        products = hxs.select(u'//b[contains(text(), "\xa3")]/../..')

        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            product_loader.add_xpath('name', './b/font/text()')
            product_loader.add_value('url', response.url)
            price = product.select(u'.//b[contains(text(), "\xa3")]/text()').re('\xa3(.*[0-9])')
            if not price:
                continue
            product_loader.add_value('price', price)
            yield product_loader.load_item()
