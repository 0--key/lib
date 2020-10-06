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

class CastoramaSpider(BaseSpider):
    name = 'castorama.fr'
    allowed_domains = ['www.castorama.fr', 'castorama.fr']
    start_urls = ('http://www.castorama.fr/store/Pistolet-a-peinture-electrique-et-machine-a-peindre-cat_id_1635.htm?navCount=8&navAction=push',
                  'http://www.castorama.fr/store/Outillage-cat_id_1584.htm?navAction=jump',
                  'http://www.castorama.fr/store/Aspirateur-et-nettoyeur-cat_id_1585.htm?navAction=jump',
                  'http://www.castorama.fr/store/Chauffage-climatisation--traitement-de-lair-cat_id_307.htm?navAction=jump',
                  'http://www.castorama.fr/store/Etabli-et-Rangement-garage-cave-atelier-cat_id_3040.htm?navAction=jump',
                  'http://www.castorama.fr/store/Construction-et-materiaux-cat_id_472.htm?navAction=jump',
                  'http://www.castorama.fr/store/Plomberie-et-traitement-de-leau-cat_id_2267.htm?navAction=jump',
                  'http://www.castorama.fr/store/Outil-a-moteur-cat_id_1456.htm?navAction=jump',
                  'http://www.castorama.fr/store/Outil-a-main-cat_id_1379.htm?navAction=jump',
                  'http://www.castorama.fr/store/Arrosage-et-recuperation-de-leau-cat_id_30.htm?navAction=jump')

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
                    return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//div[contains(@class,"productsListItem")]//h2/a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pagination
        next_page = hxs.select(u'//div[@class="suivantDivProds"]/a[@class="suivant"]/@href').extract()
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

        featured_product = hxs.select(u'//div[@class="featuredProduct"]')
        product_loader = ProductLoader(item=Product(), selector=featured_product)
        url = featured_product.select(u'.//div[@class="fDescription"]/a/@href').extract()
        if url:
            url = urljoin_rfc(get_base_url(response), url[0])
            product_loader.add_value('url', url)
            product_loader.add_xpath('name', u'.//div[@class="fDescription"]/a/strong/text()')
            price_css_classes = [{'tag': 'span', 'class': 'newprice'}, {'tag': 'div', 'class': 'price'}]
            for price_css_class in price_css_classes:
                price = featured_product.select(u'.//' + price_css_class['tag'] + '[@class="' + price_css_class['class'] + '"]/text()').re(u'([0-9\,\.]+)')
                if price:
                    price = re.sub(',', '.', price[0])
                    product_loader.add_value('price', price)
                    break
            yield product_loader.load_item()

        products = hxs.select(u'//div[contains(@class,"productsRow")]/div[contains(@class,"productItem")]')
        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            url = product.select(u'.//div[@class="prodDecription"]/a/@href').extract()
            if not url:
                continue
            url = urljoin_rfc(get_base_url(response), url[0])
            product_loader.add_value('url', url)
            product_loader.add_xpath('name', u'.//div[@class="prodDecription"]/a/text()')
            price_css_classes = [{'tag': 'span', 'class': 'newprice'}, {'tag': 'div', 'class': 'price'}]
            for price_css_class in price_css_classes:
                price = product.select(u'.//' + price_css_class['tag'] + '[@class="' + price_css_class['class'] + '"]/text()').re(u'([0-9\,\.]+)')
                if price:
                    price = re.sub(',', '.', price[0])
                    product_loader.add_value('price', price)
                    break
            yield product_loader.load_item()

        if not products or not featured_product:
            log.msg('Retrying url: %s' % response.url, level=log.WARNING)
            retries = response.meta.get('retries', 0)
            if retries < 3:
                yield Request(response.url, dont_filter=True, meta={'retries': retries + 1})
