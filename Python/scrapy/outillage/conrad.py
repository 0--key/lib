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

class ConradSpider(BaseSpider):
    name = 'conrad.fr'
    allowed_domains = ['www.conrad.fr', 'conrad.fr']
    start_urls = ('http://www.conrad.fr/outillage_mesure_c_53207',
                  'http://www.conrad.fr/equipement_maison_c_52080')

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
                    return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//ul[@class="sousCat" or @class="categorie"]//a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pagination
        next_page = hxs.select(u'//ul[@class="pages"]//a[@title="suivant"]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(next_page)

        # products
        for product in self.parse_product(response):
            yield product
    
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        products = hxs.select(u'//table[@class="list"]//tr')[1:]
        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            url = product.select(u'.//h3/a/@href').extract()
            url = urljoin_rfc(get_base_url(response), url[0])
            product_loader.add_value('url', url)
            product_loader.add_xpath('name', u'.//h3/a/text()')
            product_loader.add_xpath('price', u'.//p[@class="prixPromo"]/text()',
                                     re=u'([\d\.]+)')
            yield product_loader.load_item()