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

class SunriseSpider(BaseSpider):
    name = 'sunrise.ch'
    allowed_domains = ['sunrise.ch', 'www.sunrise.ch']
    start_urls = (u'http://www1.sunrise.ch/Handys-mit-Abo/Samsung-I9300-16GB-Galaxy-S3-pcQAnAqFI.cOwAAAEub1Q1nWwDWjrAqFI.FOAAAAE3rBkdczYN-Sunrise-Residential-Site-WFS-de_CH-CHF.html', )

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        for product in self.parse_product(response):
            yield product

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        for product in hxs.select(u'//div[@class="jsRateplanGroup"]/ul[starts-with(@class,"content area")]'):
            plan_types = {u'12 months': u'Short', u'24 months': u'Long'}
            for plan_type, plan_xpath in plan_types.items():
                loader = ProductLoader(item=Product(), selector=product)
                loader.add_value('url', response.url)
                name = hxs.select(u'//div[@class="floatLeft productInfo"]/h1/text()')[0].extract().strip()
                abo_name = product.select(u'./li[@class="first"]/div/text()')[0].extract().strip()
                loader.add_value('name', u'%s %s %s' % (name, abo_name, plan_type))
                price = product.select(u'.//li[@class="seventh" and @id="js%sDuration"]/div/text()' % plan_xpath)[0].extract().replace(u'\u2013', u'')
                loader.add_value('price', price)
                # if loader.get_output_value('price'):
                yield loader.load_item()
