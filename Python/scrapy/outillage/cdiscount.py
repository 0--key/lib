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

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))

class CDiscountSpider(BaseSpider):
    name = 'cdiscount.com'
    allowed_domains = ['www.cdiscount.com', 'cdiscount.com']
    start_urls = ('http://www.cdiscount.com/maison/jardin-plein-air/v-11785-11785.html',
                  'http://www.cdiscount.com/electromenager/aspirateur-nettoyeur-vapeur/v-11014-11014.html')

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
                    return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//li/a[contains(text(),"Aspirateur ")]/@href').extract()
        categories += hxs.select(u'//li[child::a[contains(text(),"Aspirateur ")]]/ul//a/@href').extract() # aspirateurs
        categories += hxs.select(u'//div[preceding-sibling::div[child::strong[contains(text(), "Plein Air")]] and \
                                following-sibling::div[child::strong[contains(text(),"Outillage")]]]//a[not(child)]/@href').extract()
        #categories += hxs.select(u'//ul[preceding-sibling::div[child::strong[contains(text(), "Plein Air")]] and \
                                #following-sibling::div[child::strong[contains(text(),"Outillage")]]]//a[not(child)]/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pagination
        next_page = hxs.select(u'//ul[@class="PaginationButtons"]//a[contains(text(),"Suivant")]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(next_page)

        # products
        products = hxs.select(u'//div[contains(@class,"productCell") or contains(@class,"productLine")]//a/@href').extract()
        products += hxs.select(u'//div[contains(@id,"tabContent0")]//div[contains(@class,"product100")]//a/@href').extract()
        products += hxs.select(u'//div[contains(@class,"productHomeListBody")]//a/@href').extract()
        products = [url for url in products if url != '#']
        products = set(products)
        for url in products:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product)
    
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        product_loader = ProductLoader(item=Product(), response=response)
        product_loader.add_value('url', response.url)
        product_loader.add_xpath('name', u'//h1[contains(@class,"fpProdutTitle")]/text()')
        price = hxs.select(u'//div[contains(@class,"priceContainer")]/div[contains(@class,"priceXL")]/text()').extract()
        if price:
            price = price[0] + '.' + hxs.select(u'//div[contains(@class,"priceContainer")]/div[contains(@class,"priceXL")]/sup/text()').re(u'(\d+)')[0]
            product_loader.add_value('price', price)
        if product_loader.get_output_value('name') and product_loader.get_output_value('price'):
            yield product_loader.load_item()
