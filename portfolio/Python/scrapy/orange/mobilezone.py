import re
import os
import json

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse, TextResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode
import hashlib
from decimal import Decimal

import csv

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))

class MobileZoneSpider(BaseSpider):
    name = 'mobilezone.ch'
    allowed_domains = ['mobilezone.ch', 'www.mobilezone.ch']
    start_urls = (u'http://www.mobilezone.ch/mobiltelefone/10742-samsung-gt-i9300-galaxy-s-iii-16gb-pebble-blue?tab=top10', )

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        product_name = hxs.select(u'//div[@id="data"]/h1/text()')[0].extract().strip()

        url = u'http://www.mobilezone.ch/mobiltelefone/extras/?extras_tab=offers_new'
        yield Request(url, callback=self.parse_product, meta={'product_name': product_name, 'product_url': response.request.url})


    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        providers = hxs.select(u'//div[@class="provider"]')
        for provider in providers[0:-1]:
            provider_name = provider.select(u'./preceding-sibling::h3[1]/a/text()')[0].extract().strip().split(' ')[0]
            for product in provider.select(u'.//tr[@class="content"]'):
                for abo_time in enumerate([u'12 Monate', u'24 Monate'], 1):
                    loader = ProductLoader(item=Product(), selector=product)
                    loader.add_value('url', response.meta['product_url'])
                    abo_name = product.select(u'./td[@class="name"]/text()')[0].extract().strip()
                    name = u'%s %s %s %s' % (response.meta['product_name'], provider_name, abo_name, abo_time[1])
                    loader.add_value('name', name)
                    price = product.select(u'./td[@class="price"][%s]/label/text()' % str(abo_time[0]))[0].extract().replace(u'\u2013', u'')
                    loader.add_value('price', price)
                    # if loader.get_output_value('price'):
                    yield loader.load_item()
