#!/usr/bin/python
# -*- coding: latin-1 -*-

import csv
import os
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.fuzzywuzzy import process
from product_spiders.fuzzywuzzy import fuzz

HERE = os.path.abspath(os.path.dirname(__file__))

class JbhifiSpider(BaseSpider):
    name = 'jbhifi.com.au'
    allowed_domains = ['jbhifi.com.au', 'jbhifionline.com.au']
    start_urls = ['http://www.jbhifionline.com.au']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        relative_urls = hxs.select('//*[@id="outernavigation"]/table/tr/td/a/@href').extract()
        for relative_url in relative_urls:
            url = urljoin_rfc(get_base_url(response), relative_url)
            yield Request(url, callback=self.parse_subcategories)
    
    def parse_subcategories(self, response):
        hxs = HtmlXPathSelector(response)
        relative_urls = hxs.select('//*[@id="leftNav"]/div[@class="sidenav"]/ul/li/a/@href').extract()
        for relative_url in relative_urls:
            url = urljoin_rfc(get_base_url(response), relative_url)
            yield Request(url, callback=self.parse_products)
        
    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="result_container"]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', 'div/div/div/div/h1/a/text()')
            url = urljoin_rfc(get_base_url(response), product.select('div/div/div/div/h1/a/@href').extract()[0])
            loader.add_value('url', url)
            loader.add_xpath('price', 'div//div[@class="price-image-layer"]/img/@alt')
            yield loader.load_item()
        next = hxs.select('//div[@class="CatNavigation"]/a[text()="»"]/@href'.decode('utf')).extract()
        if next:
            url = urljoin_rfc(get_base_url(response), next[0])
            yield Request(url, callback=self.parse_products)

    
