import re
import os
from decimal import Decimal

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

class japanesekoi_spider(BaseSpider):
    name = 'japanese-koi.co.uk'
    allowed_domains = ['japanese-koi.co.uk', 'www.japanese-koi.co.uk']
    start_urls = ('http://www.japanese-koi.co.uk/',)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//div[@class="store-switcher"]//a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        subcategories = hxs.select(u'//div[@class="col-left sidebar"]//a/@href').extract()
        subcategories += hxs.select(u'//ul[@class="category-grid"]//a/@href').extract()
        for url in subcategories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)


        # pagination
        next_page = hxs.select(u'//a[@class="next i-next"]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(next_page)

        # products
        products = hxs.select(u'//ul[@class="products-grid"]//a/@href').extract()
        for url in products:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product)

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        name = hxs.select(u'//div[@class="product-name"]/h1/text()').extract()[0]
        base_price = hxs.select(u'//p[@class="special-price"]/span[@class="price"]/text()').extract()
        if not base_price:
            base_price = hxs.select(u'//span[@class="regular-price"]/span[@class="price"]/text()').extract()
        base_price = base_price[0]
        product_options = hxs.select(u'//ul[@class="options-list"]/li')
        if product_options:
            for option in product_options:
                loader = ProductLoader(item=Product(), response=response)
                loader.add_value('url', response.url)
                name_with_option = name + u' %s' % option.select(u'./span[@class="label"]/label/text()').extract()[0]
                loader.add_value('name', name_with_option)
                extra_price = option.select(u'./span[@class="label"]/label/span/span/text()').extract()
                if extra_price:
                    extra_price = extra_price[0].replace(u'\xa3', u'')
                base_price = base_price.replace(u'\xa3', u'')
                loader.add_value('price', Decimal(base_price) + (Decimal(extra_price) if extra_price else Decimal('0.00')))
                if loader.get_output_value('price'):
                    yield loader.load_item()
        else:

            loader = ProductLoader(item=Product(), response=response)
            loader.add_value('url', response.url)
            loader.add_value('name', name)
            loader.add_value('price', base_price)
            if loader.get_output_value('price'):
                yield loader.load_item()