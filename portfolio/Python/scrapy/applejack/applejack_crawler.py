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

class AppleJackSpider(BaseSpider):
    name = 'applejack.com'
    allowed_domains = ['www.applejack.com', 'applejack.com']
    start_urls = ()

    def __init__(self, *args, **kwargs):
        super(AppleJackSpider, self).__init__(*args, **kwargs)
        self.skus = set()
        with open(os.path.join(HERE, 'applejack_skus.csv'), 'rb') as f:
            reader = csv.reader(f)
            reader.next()
            for row in reader:
                self.skus.add(row[0])


    def start_requests(self):
        search_url = u'http://www.applejack.com/search/?criteria=%s&product_category=wine%%2Cspirits%%2Cbeer%%2Ccordials_liqueurs&x=0&y=0'
        for sku in self.skus:
            yield Request(search_url % sku, dont_filter=True, meta={'sku': sku})


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # pagination
        # next_page = hxs.select(u'//a[@title="Next Page"]/@href').extract()
        # if next_page:
            # next_page = urljoin_rfc(get_base_url(response), next_page[0])
            # yield Request(next_page, meta=response.meta)

        # products
        products = hxs.select(u'//div[@class="productcatalog-search-result"]/h4/a/@href').extract()
        for url in products:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, meta=response.meta, dont_filter=True, callback=self.parse_product)
    
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        loader = ProductLoader(item=Product(), response=response)
        loader.add_value('url', response.url)
        loader.add_value('sku', re.search('product/(\d+)', response.url).groups())
        name = hxs.select(u'//h1[@class="pagetitle"]/text()').extract()[0].strip()
        bottle_size = hxs.select(u'//div[child::strong[contains(text(), "Bottle Size") or contains(text(), "Size of Bottle")]]/span/text()')
        if not bottle_size:
            bottle_size = hxs.select(u'//div[contains(text(),"Size of Bottle")]/span/text()')
        name += ' ' + bottle_size.extract()[0].strip()
        loader.add_value('name', name)
        loader.add_xpath('price', u'//div[@class="cardPrice"]/text()')
        if not loader.get_output_value('price'):
            loader.add_xpath('price', u'//div[@class="salePrice"]/text()')
        if not loader.get_output_value('price'):
            loader.add_xpath('price', u'//div[@class="regularPrice"]/text()')
        if not loader.get_output_value('price'):
            loader.add_xpath('price', u'//div[@class="regularprice"]/text()')
        site_sku = hxs.select(u'//span[@class="itemnumber"]/text()').re(u'- (.*)')[0].strip()
        search_sku = response.meta['sku'].strip()
        if site_sku == search_sku:
            yield loader.load_item()
