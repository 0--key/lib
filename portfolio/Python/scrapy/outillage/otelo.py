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

from product_spiders.items import Product, ProductLoader
from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))

class OteloSpider(BaseSpider):
    name = 'otelo.fr'
    allowed_domains = ['www.otelo.fr', 'otelo.fr']
    start_urls = ('http://www.otelo.fr/fr/catalogue/soudage-brasage',
                  'http://www.otelo.fr/fr/catalogue/fluides-air-comprime-lubrification',
                  'http://www.otelo.fr/fr/catalogue/equipements-electriques',
                  'http://www.otelo.fr/fr/catalogue/elements-fixation/agrafeuses-cloueurs',
                  'http://www.otelo.fr/fr/catalogue/manutention-expeditions-levage',
                  'http://www.otelo.fr/fr/catalogue/equipements-stockage',
                  'http://www.otelo.fr/fr/catalogue/travail-du-bois',
                  'http://www.otelo.fr/fr/catalogue/hygiene-securite',
                  'http://www.otelo.fr/fr/catalogue/machines-outils',
                  'http://www.otelo.fr/fr/catalogue/outils-main-electroportatifs')

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
                    return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//div[@class="classificationBoxContain"]//a[@class="BoxClassifLink"]/@href').extract()
        for url in categories:
            yield Request(url)

        # pagination
        next_page = hxs.select(u'//a[@id="skugroupsBtnNextPage"]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(next_page)

        # products
        products = hxs.select(u'//a[@class="BoxSkuGroupLink"]/@href').extract()
        for url in products:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        for product in self.parse_product(response):
            yield product
    
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        multiple_products = hxs.select(u'//table[@id="ListeSkuGroupTableGauche"]//a/@href').extract()
        for url in multiple_products:
            yield Request(url)

        product_loader = ProductLoader(item=Product(), response=response)
        product_loader.add_value('url', response.url)
        name = hxs.select(u'//h1[@id="sku_Title"]/text()').extract()
        if not name:
            return
        brand = hxs.select(u'//h1[@id="sku_Title"]/span[@id="sku_Brand"]/text()').extract()
        if brand:
            name = brand[0] + ' ' + name[0].strip()
        else:
            name = name[0].strip()
        sku = hxs.select(u'//div[@class="sku_TP_TD"]/div[@class="sku_TP_SKU"]/text()').extract()
        if sku:
            name += ' (' + sku[0].strip() + ')'
        product_loader.add_value('name', name)
        price = hxs.select(u'//div[@id="sku_ZonePriceNormal"]//div[@id="sku_ZPN_HT"]/text()').re(u'([\d\.,]+)')
        if price:
            price = re.sub(',', '.', price[0])
            product_loader.add_value('price', price)
            if product_loader.get_output_value('name') and not multiple_products:
                yield product_loader.load_item()