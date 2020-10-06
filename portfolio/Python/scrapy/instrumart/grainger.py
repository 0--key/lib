import re
import json
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.utils import extract_price

HERE = os.path.dirname(os.path.abspath(__file__))

class GraingerSpider(BaseSpider):
    name = 'grainger.com'
    allowed_domains = ['grainger.com']
    #start_urls = ('http://www.grainger.com/Grainger/ecatalog/N-/Ntt-?itemsPerPage=60',)

    def start_requests(self):
        with open(os.path.join(HERE, 'graingercats')) as f:
            urls = f.read().split()
            for url in urls:
                yield Request(url)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        pages = hxs.select('//span[@class="paginationContainer"]//a/@href').extract()
        for page in pages:
            yield Request(page)

        for product in self.parse_products(hxs, response):
            yield product

    def parse_products(self, hxs, response):
        products = hxs.select('//table[@class="esr_itemListTable"]'+
                              '//tr[contains(@class, "Row")]//div[@class="pirce"]/../..')
        for product in products:
            loader = ProductLoader(selector=product, item=Product())
            loader.add_xpath('url', './/div[@gwtype="overflowRegion"]//a/@href')
            loader.add_xpath('name', './/div[@gwtype="overflowRegion"]//a/text()')
            loader.add_xpath('price', './/div[@class="pirce"]/text()')
            yield loader.load_item()
