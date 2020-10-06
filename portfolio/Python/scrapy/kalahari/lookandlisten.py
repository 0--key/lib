import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode
from scrapy import log

import csv

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class LookAndListenSpider(BaseSpider):
    name = 'lookandlisten.co.za'
    allowed_domains = ['lookandlisten.co.za']
    download_delay = 0.5

    def start_requests(self):
        with open(os.path.join(HERE, 'products.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ProductType'] == 'Books':
                    continue

                sku = row['ProdCode']

                title = row['Title']
                url = 'http://www.lookandlisten.co.za/search/%s/All/'
                yield Request(url % title.replace(' ', '+'), meta={'sku': sku})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        cats = hxs.select('//div[@id="recommendsTabs"]//li/a/@href').extract()

        for cat in cats:
            yield Request(urljoin_rfc(get_base_url(response), cat), callback=self.parse_products,
                          meta={'sku': response.meta['sku']})

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)

        prods = list(set(hxs.select('//a[starts-with(@href, "/view/")]/@href').extract()))

        if prods:
            yield Request(urljoin_rfc(get_base_url(response), prods[0]),
                          callback=self.parse_product,
                          meta={'sku': response.meta['sku'], 'products': prods[1:]})

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)

        loader = ProductLoader(item=Product(), response=response)
        loader.add_xpath('name', '//div[@class="CB_box_prodview"]//h2/text()')
        loader.add_value('url', response.url)
        price = ''.join(hxs.select('//div[@class="viewprod_price"]//text()').extract())
        loader.add_value('price', price)
        loader.add_xpath('sku', '//div[@class="viewprod_right"]//div/text()', re='Barcode: (.*)')

        log.msg(loader.get_output_value('sku'))
        log.msg(response.meta['sku'])

        if loader.get_output_value('sku') == response.meta['sku']:
            yield loader.load_item()
        else:
            prods = response.meta['products']
            if prods:
                yield Request(urljoin_rfc(get_base_url(response), prods[0]),
                              callback=self.parse_product,
                              meta={'sku': response.meta['sku'], 'products': prods[1:]})