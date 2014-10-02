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

class ScrewfixSpider(BaseSpider):
    name = 'test-screwfix.com'
    allowed_domains = ['screwfix.com', 'competitormonitor.com']

    def __init__(self, *args, **kwargs):
        super(ScrewfixSpider, self).__init__(*args, **kwargs)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        if spider.name == self.name:
            shutil.copy('data/%s_products.csv' % spider.crawl_id, os.path.join(HERE, 'screwfix_products.csv'))

    def start_requests(self):
        if self.full_run_required():
            start_req = self._start_requests_full()
            log.msg('Full run')
        else:
            start_req = self._start_requests_simple()
            log.msg('Simple run')

        for req in start_req:
            yield req

    def _start_requests_full(self):
        yield Request('http://www.screwfix.com/', callback=self.parse_full)

    def _start_requests_simple(self):
        yield Request('http://competitormonitor.com/login.html?action=get_products_api&website_id=470333&matched=1',
                      callback=self.parse_simple)

    def full_run_required(self):
        if not os.path.exists(os.path.join(HERE, 'screwfix_products.csv')):
            return True

        #run full only on Mondays
        return datetime.now().weekday() == 1

    def parse_full(self, response):
        hxs = HtmlXPathSelector(response)

        cats = hxs.select('//ul[@id="main-nav"]//a/@href').extract()
        for cat in cats:
            yield Request(urljoin_rfc(get_base_url(response), cat), callback=self.parse_subcats_full)

    def parse_subcats_full(self, response):
        hxs = HtmlXPathSelector(response)

        subcats = hxs.select('//a[@class="range_links"]/@href').extract()
        subcats += hxs.select('//a[@forsubcatid]/@href').extract()

        for cat in subcats:
            yield Request(urljoin_rfc(get_base_url(response), cat), callback=self.parse_subcats_full)

        for product in self.parse_products(hxs):
            yield product

    def parse_products(self, hxs):
        products = hxs.select('//div[@class="product-info"]')

        for product in products:
            self.prods_count += 1
            loader = ProductLoader(selector=product, item=Product())
            loader.add_xpath('name', './/a[starts-with(@id, "product_description")]/text()')
            loader.add_xpath('url', './/a[starts-with(@id, "product_description")]/@href')
            loader.add_xpath('price', '//em[starts-with(@id, "product_list_price")]/text()')

            yield loader.load_item()

    def parse_simple(self, response):
        f = StringIO.StringIO(response.body)
        hxs = HtmlXPathSelector()
        reader = csv.DictReader(f)
        self.matched = set()
        for row in reader:
            self.matched.add(row['url'])

        for url in self.matched:
            yield Request(url, self.parse_product)

        with open(os.path.join(HERE, 'screwfix_products.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['url'] not in self.matched:
                    loader = ProductLoader(selector=hxs, item=Product())
                    loader.add_value('url', row['url'])
                    loader.add_value('sku', row['sku'])
                    loader.add_value('identifier', row['identifier'])
                    loader.add_value('name', row['name'])
                    loader.add_value('price', row['price'])
                    yield loader.load_item()

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        loader = ProductLoader(item=Product(), selector=hxs)
        loader.add_value('url', response.url)
        loader.add_xpath('name', '//h1[@itemprop="name"]/text()')
        loader.add_xpath('price', '//span[@itemprop="price"]/text()')

        yield loader.load_item()
