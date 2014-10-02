#!/usr/bin/python
# -*- coding: latin-1 -*-

import csv
import os
from scrapy import log
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.fuzzywuzzy import process
from product_spiders.fuzzywuzzy import fuzz

HERE = os.path.abspath(os.path.dirname(__file__))

class WearepetsSpider(BaseSpider):
    name = 'wearepets.co.uk'
    allowed_domains = ['wearepets.co.uk']
    start_urls = ['http://www.wearepets.co.uk/sitemap']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//*[@id="ThreeColMiddle"]/ul/li/a/@href ').extract()
        for category in categories:
            url =  urljoin_rfc(get_base_url(response), category)
            yield Request(url, callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//li[@class="item" or @class="item lastItem"]')
        for product in products:
            name = product.select('div/h3/a/span/text()').extract()[0]
            url = product.select('div/h3/a/@href').extract()
            if url:
                url =  urljoin_rfc(get_base_url(response), url[0])
            options_from = ''.join(product.select('div/p[@class="price money"]/span/abbr/text()').extract()).strip()
            options_now = ''.join(product.select('div/p[@class="price money"]/text()').extract()).strip()
            if ('From' in options_from) or ('Now' in options_now):
                yield Request(url, callback=self.parse_options, meta={'name':name})
            else:
                loader = ProductLoader(item=Product(), selector=product)   
                loader.add_value('name', name)
                loader.add_value('url', url)
                price = product.select('div/p[@class="price money"]/span/span/text()').extract()
                if not price:
                    price = product.select('div/p[@class="price money"]/ins/span/text()').extract()                  
                    if not price:
                        price = ['']
                loader.add_value('price', price[0])
                yield loader.load_item()
        next = hxs.select('//a[@rel="nofollow" and span/text()="Next \xc2\xbb"]/@href'.decode('utf')).extract()
        if next:
            url =  urljoin_rfc(get_base_url(response), next[0])
            yield Request(url, callback=self.parse_products)
        else:
            sub_categories = hxs.select('//*[@id="categoryNavigation"]/li/ul/li/a/@href').extract()
            for sub_category in sub_categories:
                url =  urljoin_rfc(get_base_url(response), sub_category)
                yield Request(url, callback=self.parse_products)

    def parse_options(self, response):
        hxs = HtmlXPathSelector(response)
        options = hxs.select('//*[@id="pv_id"]/option/text()').extract()
        if options:
            for option in options:
                loader = ProductLoader(item=Product(), response=response)   
                name, price = option.split('- £'.decode('utf'))
                loader.add_value('name', ' '.join((response.meta['name'], name)))
                loader.add_value('url', response.url)
                loader.add_value('price', price)
                yield loader.load_item()
        else:
            loader = ProductLoader(item=Product(), response=response)
            loader.add_value('name', response.meta['name'])
            loader.add_value('url', response.url)
            price = ''.join(hxs.select('//div[@class="item"]/div/form/fieldset/p/span[@class="amount"]/text()').extract())
            if not price:
                price = ''.join(hxs.select('//div[@class="item"]/div/form/fieldset/p/ins/span[@class="amount"]/text()').extract())
            loader.add_value('price', price)
            yield loader.load_item()
          
