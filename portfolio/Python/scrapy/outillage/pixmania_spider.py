#!/usr/bin/python
# -*- coding: latin-1 -*-

import os
from scrapy import log
from scrapy.http import Request
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

URLS = {"http://www.pixmania.com/fr/fr/jardin/44/onglet.html": "Jardin",
        "http://www.pixmania.com/fr/fr/bricolage/115/onglet.html": "Bricolage",
        "http://www.pixmania.com/aspirateur-et-nettoyeur/frfr45_443_pm.html": "Aspirateur et nettoyeur", 
        "http://www.pixmania.com/arrosage/frfr44_2043_pm.html": "Arrosage",
        "http://www.pixmania.com/outillage-a-main/frfr44_2042_pm.html": "Outillage à main",
        "http://www.pixmania.com/outillage-motorise/frfr44_2041_pm.html": "Outillage motorisé"}

class PixmaniaSpider(BaseSpider):
    name = "pixmania.com"
    allowed_domains = ["pixmania.com"]
    start_urls = URLS.keys()

    def parse(self, response):
        urls = URLS
 
        hxs = HtmlXPathSelector(response)
        links_div = hxs.select(u'//div[@class="box box-nav box-universe-nav" and strong[text()="'+ urls[response.url].decode('utf8')+'"]]'.decode('utf8'))

        sites = links_div.select('ul/li[not(@class="highlight")]/a/@href')          
        for site in sites:
            first_url =  site.extract()
            url = urljoin_rfc(first_url, '?sPageInfo=0', response.encoding)
            yield Request(url, callback = self.parse_categories)

    def parse_categories(self, response):
        hxs = HtmlXPathSelector(response)
        if hxs.select('//span[@class="nav-landmark"]/text()'):
            total_pages = int(hxs.select('//span[@class="nav-landmark"]/text()').extract()[0].split()[-1])
            for i in range(total_pages):
                url = self._urljoin(response,'?sPageInfo=%s' % i)
                yield Request(url, callback = self.parse_products)
        else:
            name = hxs.select('//div/div/div/div/div/h1/text()').extract()[0]
            links_div = hxs.select(u'//div[@class="box box-nav box-universe-nav" and strong[text()="'+ name +'"]]'.decode('utf8'))
            sites = links_div.select('ul/li[not(@class="highlight")]/a/@href')
            for site in sites:
                url =  site.extract()
                yield Request(url, callback = self.parse_categories)


    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//*[@id="area-2"]//div[@class="grid-25"]')
        if products:
            for product in products:
                loader = ProductLoader(item=Product(), selector=product)
                loader.add_xpath('url', 'div/h3/a/@href')
                if product.select('div/h3/a/abbr/@title'):
                    loader.add_xpath('name', 'div/h3/a/abbr/@title')
                else:
                    loader.add_xpath('name','div/h3/a/text()')
                price = product.select('div/div/p[@class="prd-amount"]/strong/text()').extract()[0]
                loader.add_value('price', self._encode_price(price))
                yield loader.load_item()
        else:
            products = hxs.select('//*[@id="area-2"]//tr[@class="prd first"]')
            for product in products:
                loader = ProductLoader(item=Product(), selector=product)
                loader.add_xpath('url', 'td/h3/a/@href')
                loader.add_xpath('name', 'td/h3/a/text()')
                if product.select('td/p/strong/text()').extract():
                    price = product.select('td/p/strong/text()').extract()[0]
                else:
                    if product.select('td/div/p/strong/text()').extract():
                        price = product.select('td/div/p/strong/text()').extract()[0]
                loader.add_value('price', self._encode_price(price))
                yield loader.load_item()

        

    def _urljoin(self, response, url):
        """Helper to convert relative urls to absolute"""
        return urljoin_rfc(response.url, url, response.encoding)

    def _encode_price(self, price):
        return price.replace(',','.').encode("ascii","ignore")
