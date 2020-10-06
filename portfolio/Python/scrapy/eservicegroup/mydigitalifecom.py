# -*- coding: utf-8 -*-

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.utils.response import get_base_url
from scrapy.http import Request

from product_spiders.items import ProductLoader, Product

import urlparse

__author__ = 'Theophile R. <rotoudjimaye.theo@gmail.com>'

class MyDigitalLifeSpider(BaseSpider):
    name = "mydigitaland.com"
    allowed_domains = ["mydigitaland.com"]
    start_urls = ["http://www.mydigitaland.com/"]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        for href in hxs.select("//ul[@id='nav-sidebox']/li/a/@href").extract():
            yield Request(urlparse.urljoin(base_url, href)+"?limit=all", callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)

        for product_box in hxs.select('//div[@class="category-products"]/ul/li'):
            product_loader = ProductLoader(item=Product(), selector=product_box)

            product_loader.add_xpath('name', './/h2[@class="product-name"]/a/text()')
            product_loader.add_xpath('url', './/h2[@class="product-name"]/a/@href')
            product_loader.add_xpath('price', './/p[@class="special-price"]//span[@class="price"]/text()')

            yield product_loader.load_item()
