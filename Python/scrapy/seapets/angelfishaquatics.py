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

class angelfishaquatics_spider(BaseSpider):
    name = 'angelfishaquatics.co.uk'
    allowed_domains = ['angelfishaquatics.co.uk', 'www.angelfishaquatics.co.uk']
    start_urls = ('http://www.angelfishaquatics.co.uk/',)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//div[@class="navigation-inner"]//a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        subcategories = hxs.select(u'//div[@class="category-wrap"]//a/@href').extract()
        for url in subcategories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)


        # pagination
        # next_page = hxs.select(u'').extract()
        # if next_page:
            # next_page = urljoin_rfc(get_base_url(response), next_page[0])
            # yield Request(next_page)

        # products
        products = hxs.select(u'//div[@class="product-wrap"]//a/@href').extract()
        for url in products:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product)

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        name = hxs.select(u'//div[@class="product-right"]//div[@class="pp-name"]/h1/text()').extract()[0].strip()
        main_price = hxs.select(u'//div[@class="product-right"]//div[@class="pp-price"]/span/span/text()').extract()[0]
        product_options = hxs.select(u'//select[@class="ekm-productoptions-dropdown-option"]')
        if product_options:
            body = response.body.replace('\xc2', ' ')
            if product_options.select(u'../select[@onchange]'):
                set_option_price = True
            for option in product_options.select(u'./option'):
                name_with_option = name + u' %s' % option.select(u'./text()').extract()[0].strip()
                option_value = option.select(u'./@value').extract()[0]
                price = re.search('== \'%s\'.*?_EKM_PRODUCTPRICE.*?= \'([\d\.]+?)\'' % option_value, body, re.DOTALL).groups()[0]\
                        if set_option_price else main_price

                loader = ProductLoader(item=Product(), response=response)
                loader.add_value('name', name_with_option)
                loader.add_value('price', price)
                loader.add_value('url', response.url)
                if loader.get_output_value('price'):
                    yield loader.load_item()
        else:
            loader = ProductLoader(item=Product(), response=response)
            loader.add_value('url', response.url)
            loader.add_value('name', name)
            loader.add_value('price', main_price)
            if loader.get_output_value('price'):
                yield loader.load_item()