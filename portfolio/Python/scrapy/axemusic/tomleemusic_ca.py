import re
import logging
import urllib
import csv
import os
import shutil
from datetime import datetime
import StringIO

from scrapy.spider import BaseSpider
from scrapy import signals
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.xlib.pydispatch import dispatcher
from scrapy.exceptions import CloseSpider

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

from scrapy import log
HERE = os.path.abspath(os.path.dirname(__file__))

class TomLeeMusicCaSpider(BaseSpider):
    name = 'tomleemusic.ca'
    allowed_domains = ['tomleemusic.ca', 'competitormonitor.com']

    def __init__(self, *args, **kwargs):
        super(TomLeeMusicCaSpider, self).__init__(*args, **kwargs)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def start_requests(self):
        if self.full_run_required():
            start_req = self._start_requests_full()
            log.msg('Full run')
        else:
            start_req = self._start_requests_simple()
            log.msg('Simple run')

        for req in start_req:
            yield req

    def spider_closed(self, spider):
        if spider.name == self.name:
            shutil.copy('data/%s_products.csv' % spider.crawl_id, os.path.join(HERE, 'tomleemusic_products.csv'))

    def _start_requests_full(self):
        yield Request('http://www.tomleemusic.ca/main/products.cfm', callback=self.parse_full)

    def _start_requests_simple(self):
        yield Request('http://competitormonitor.com/login.html?action=get_products_api&website_id=470333&matched=1',
                      callback=self.parse_simple)

    def full_run_required(self):
        if not os.path.exists(os.path.join(HERE, 'tomleemusic_products.csv')):
            return True

        #run full only on Mondays
        return datetime.now().weekday() == 1

 
    def parse_full(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//a[@class="catLink"]/@href').extract():
            yield Request(url, callback=self.parse_product_list)

    def parse_product_list(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//a[@class="catLink"]/@href').extract():
            yield Request(url, callback=self.parse_product_list)
 
        for url in hxs.select(u'//a[@class="productListLink"]/@href').extract():
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product)

        next_page = hxs.select(u'//a[@class="smallPrint" and contains(text(),"Next")]/@href').extract()
        if next_page:
            url = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(url, callback=self.parse_product_list)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)

        product_loader = ProductLoader(item=Product(), selector=hxs)
        product_loader.add_value('url', response.url)
        product_loader.add_xpath('name', u'//h1[@class="productDetailHeader"]/text()')
        if hxs.select(u'//span[@class="productDetailSelling"]/text()'):
            product_loader.add_xpath('price', u'//span[@class="productDetailSelling"]/text()')
        else:
            product_loader.add_value('price', '')
        product_loader.add_xpath('sku', u'//input[@type="hidden" and (@name="hidProductId" or @name="inv")]/@value')
        product_loader.add_xpath('category', u'//td[@class="smallPrint"]/a[position()=2 and contains(text(),"Products")]/../a[3]/text()')

        img = hxs.select(u'//a[@class="smallPrint" and @rel="lightbox"]/@href').extract()
        if img:
            img = urljoin_rfc(get_base_url(response), img[0])
            product_loader.add_value('image_url', img)
        if hxs.select(u'//a[contains(@href,"BrandName")]/@href'):
            product_loader.add_xpath('brand', u'substring-after(//a[contains(@href,"BrandName")]/@href,"=")')
        else:
            brands = hxs.select(u'//strong[@class="sideBarText"]/text()').extract()
            brands = [b.strip() for b in brands]
            for brand in brands:
                if product_loader.get_output_value('name').startswith(brand):
                    product_loader.add_value('brand', brand)
                    break
            else:
                product_loader.add_xpath('brand', u'normalize-space(substring-before(substring-after(//title/text(), " - "), " - "))')
#        product_loader.add_xpath('shipping_cost', u'//div[@class="DetailRow"]/div[contains(text(),"Shipping")]/../div[2]/text()')

        yield product_loader.load_item()

    def parse_simple(self, response):
        f = StringIO.StringIO(response.body)
        hxs = HtmlXPathSelector()
        reader = csv.DictReader(f)
        self.matched = set()
        for row in reader:
            self.matched.add(row['url'])

        for url in self.matched:
            yield Request(url, self.parse_product)

        with open(os.path.join(HERE, 'tomleemusic_products.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['url'] not in self.matched:
                    loader = ProductLoader(selector=hxs, item=Product())
                    loader.add_value('url', row['url'])
                    loader.add_value('sku', row['sku'])
                    loader.add_value('identifier', row['identifier'])
                    loader.add_value('name', row['name'])
                    loader.add_value('price', row['price'])
                    loader.add_value('category', row['category'])
                    loader.add_value('brand', row['brand'])
                    loader.add_value('image_url', row['image_url'])
                    loader.add_value('shipping_cost', row['shipping_cost'])
                    yield loader.load_item()
