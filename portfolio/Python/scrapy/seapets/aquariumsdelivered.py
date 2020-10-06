import re
import os
import json

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode
import hashlib
from decimal import Decimal

import csv

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))

class aquariumsdelivered_spider(BaseSpider):
    name = 'aquariumsdelivered.co.uk'
    allowed_domains = ['aquariumsdelivered.co.uk', 'www.aquariumsdelivered.co.uk']
    start_urls = ('http://www.aquariumsdelivered.co.uk/',)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//nav[@id="menu"]//a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url + u'?limit=all')

        # pagination
        next_page = hxs.select(u'//a[@class="next i-next"]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(next_page)

        # products
        products = hxs.select(u'//ul[contains(@class,"products-grid")]//li[contains(@class,"item")]//h2[@class="product-name"]/a/@href').extract()
        for url in products:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product)

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        options = hxs.select(u'//script').re('Product\.Bundle\((.*)\)')

        if options:
            options = json.loads(options[0])
            mandatory_options = hxs.select(u'//div[@class="input-box"]//input[@type="hidden"]')

            name = hxs.select(u'//div[@class="product-name"]/h1/text()').extract()[0].strip()
            price = Decimal(0.0)

            exclude = set()
            for mandatory_option in mandatory_options:
                option = mandatory_option.select(u'./@name').re('bundle_option\[(.*)\]')[0]
                selection = mandatory_option.select(u'./@value').extract()[0]
                option = options['options'][option]['selections'][selection]
                name += u' %s' % option['name'].strip()
                price += Decimal(option['price']).quantize(Decimal('0.01'))
                exclude.add(mandatory_option)

            option_keys = set(options['options'].keys()).difference(exclude)
            for option in option_keys:

                selection_keys = options['options'][option]['selections'].keys()
                for selection in selection_keys:
                    selection_name = options['options'][option]['selections'][selection]['name']
                    selection_price = options['options'][option]['selections'][selection]['price']
                    selection_price = Decimal(selection_price).quantize(Decimal('0.01'))

                    loader = ProductLoader(item=Product(), selector=hxs)
                    loader.add_value('url', response.url)
                    loader.add_value('name', name + u' %s' % selection_name.strip())
                    loader.add_value('price', price + selection_price)
                    if loader.get_output_value('price'):
                        yield loader.load_item()

        loader = ProductLoader(item=Product(), selector=hxs)
        loader.add_value('url', response.url)
        loader.add_xpath('name', u'//div[@class="product-name"]/h1/text()')
        loader.add_xpath('price', u'//span[@class="regular-price"]/span[@class="price"]/text()')
        if not loader.get_output_value('price'):
            loader.add_xpath('price', u'//div[@class="price-box"]//p[@class="minimal-price" or @class="price-from"]/span[@class="price"]/text()')
        if loader.get_output_value('price'):
            yield loader.load_item()
