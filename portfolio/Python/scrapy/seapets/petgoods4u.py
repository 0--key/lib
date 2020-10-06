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

class petgoods4u_spider(BaseSpider):
    name = 'petgoods4u.co.uk'
    allowed_domains = ['petgoods4u.co.uk', 'www.petgoods4u.co.uk']
    start_urls = ('http://www.petgoods4u.co.uk/',)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//ul[@id="topnav"]/li/h2/a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        subcategories = hxs.select(u'//div[@class="prod-cont" and not(child::div[@class="prod-price"])]/h2/a/@href').extract()
        for url in subcategories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

            # pagination
        # next_page = hxs.select(u'').extract()
        # if next_page:
            # next_page = urljoin_rfc(get_base_url(response), next_page[0])
            # yield Request(next_page)

        # products
        products = hxs.select(u'//div[@class="prod-cont" and child::div[@class="prod-price"]]/h2/a/@href').extract()
        for url in products:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product)

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # name = hxs.select(u'//div[@id="productDetail"]//h1[@class="productDetailTitle"]/text()').extract()[0].strip()
        # options = hxs.select(u'//td[@id="optionProductList"]')
        # if options:
            # name += u' %s' % hxs.select(u'//ul[@id="active"]/li/a/text()').extract()[0].strip()
        loader = ProductLoader(item=Product(), response=response)
        loader.add_value('url', response.url)
        loader.add_xpath('name', u'//h1[@class="product-name"]/text()')
        loader.add_xpath('price', u'//div[@class="p-prod-price"]/span/span[@class="price-alt"]/span/text()')
        if loader.get_output_value('price'):
            yield loader.load_item()

        # option_urls = hxs.select(u'//a[contains(@onclick,"changeProduct")]/@onclick').re('changeProduct\(\'(.*?)\'\)')
        # for url in option_urls:
            # url = urljoin_rfc(get_base_url(response), url)
            # yield Request(url, callback=self.parse_product)
