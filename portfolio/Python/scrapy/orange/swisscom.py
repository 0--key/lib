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

class SwisscomSpider(BaseSpider):
    name = 'swisscom.ch'
    allowed_domains = ['swisscom.ch', 'www.swisscom.ch']
    start_urls = (u'http://www.swisscom.ch/en/residential/mobile/devices/samsung-galaxy-siii-16gb-pebble-blue.html', )

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        name = hxs.select(u'//div[@class="description"]/h2/text()').extract()[0]
        product_id =  hxs.select(u'//form[@class="scs-form" and @action="/en/residential/konfiguration.html"]/input[@name="productId"]/@value').extract()[0]

        req_url = u'http://www.swisscom.ch/PortalShop/en/Configuration/DrawAbo'
        formdata = {'AboDuration': '24',
                    'HasOptions': 'False',
                    'HeaderProductId': product_id,
                    'PremiumDiscount': '0',
                    'PreselectedAbo': 'False',
                    'PreselectedCase': 'False',
                    'ProductId': product_id,
                    'ShopItem.Id': product_id,
                    'SubscriptionCase': 'New'}
        yield FormRequest(req_url, formdata=formdata, meta={'product_url': response.request.url, 'product_name': name}, callback=self.parse_product)

    def parse_product(self, response):
        if not isinstance(response, TextResponse):
            return

        res = json.loads(response.body)
        hxs = HtmlXPathSelector(text=res['Html'])

        for option in hxs.select(u'//input'):
            loader = ProductLoader(item=Product(), selector=hxs)
            loader.add_value('url', response.meta['product_url'])
            abo_name = option.select(u'./@data-display-text')[0].extract().strip()
            name = u'%s %s' % (response.meta['product_name'], abo_name)
            loader.add_value('name', name)
            price = hxs.select(u'//label[@for="%s"]/span[@class="chf-price"]/text()' % option.select(u'./@id').extract()[0])[0].extract()
            price = price.replace(u'\u2014', u'')
            loader.add_value('price', price)
            # if loader.get_output_value('price'):
            yield loader.load_item()
