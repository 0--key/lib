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

class LeroyMerlinSpider(BaseSpider):
    name = 'leroymerlin.fr'
    allowed_domains = ['www.leroymerlin.fr', 'leroymerlin.fr']
    start_urls = ('http://www.leroymerlin.fr/v3/p/produits/construction-menuiserie-l1308216916',
                  'http://www.leroymerlin.fr/v3/p/produits/terrasse-jardin-l1308216920',
                  'http://www.leroymerlin.fr/v3/p/produits/chauffage-plomberie-l1308216915',
                  'http://www.leroymerlin.fr/v3/p/produits/outillage-l1308216921',
                  'http://www.leroymerlin.fr/v3/p/produits/rangement-dressing/garage-atelier-buanderie-et-cave-l1308220643',
                  'http://www.leroymerlin.fr/v3/p/produits/quincaillerie-securite/demenagement-manutention-et-transport-l1308217025')

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
                    return
        hxs = HtmlXPathSelector(response)

        # product categories list
        categories = hxs.select(u'//div[contains(@class,"listeUniversProduits")]//h2/a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # subcategories
        subcategories = hxs.select(u'//div[@id="contentWithNavLeft"]//dt[@class="familleProduitOnline"]/a/@href').extract()
        for url in subcategories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pagination
        next_page = hxs.select(u'//ul[@class="paginationProduit"]//li[@class="noBorder"]/a[contains(text(), ">")]/@href').extract()
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

        products = hxs.select(u'//form/div[contains(@class,"highlightProduits hproduct")]')
        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            url = product.select(u'.//h3/a[@class="item url"]/@href').extract()
            url = urljoin_rfc(get_base_url(response), url[0])
            product_loader.add_value('url', url)
            product_loader.add_xpath('name', u'.//h3/a[@class="item url"]/text()')
            product_loader.add_xpath('price', u'.//p[@class="price"]/text()',
                                     re=u'([0-9\.]+)')
            if not product_loader.get_output_value('price'):
                product_loader.add_xpath('price', u'.//p[contains(@class,"price")]/text()',
                                     re=u'([0-9\.]+)')
            yield product_loader.load_item()

            if not products:
                log.msg('Retrying url: %s' % response.url, level=log.WARNING)
                retries = response.meta.get('retries', 0)
                if retries < 1:
                    yield Request(response.url, dont_filter=True, meta={'retries': retries + 1})
