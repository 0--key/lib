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

class DrillSpotSpider(BaseSpider):
    name = 'drillspot.com'
    allowed_domains = ['drillspot.com']
    #start_urls = ('http://www.drillspot.com',)

    def start_requests(self):
        with open(os.path.join(HERE, 'drillspotcats')) as f:
            urls = f.read().split()
            for url in urls:
                yield Request(url)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        '''
        if response.url == self.start_urls[0]:
            cats = hxs.select('//div[@class="sub categories"]//a/@href').extract()
            for cat in cats:
                yield Request(urljoin_rfc(get_base_url(response), cat + '?ps=120'))
        '''

        next_page = hxs.select('//li[@class="next-on"]/a/@href').extract()
        if next_page:
            yield Request(urljoin_rfc(get_base_url(response), next_page[0]))

        for product in self.parse_products(hxs, response):
            yield product

    def parse_products(self, hxs, response):
        products = hxs.select('//div[contains(@class, "product-list")]//div[@class="g-list-node"]')
        for product in products:
            loader = ProductLoader(selector=product, item=Product())
            url = urljoin_rfc(get_base_url(response), product.select('.//p[@class="name"]//a/@href').extract()[0])
            loader.add_value('url', url)
            loader.add_xpath('name', './/p[@class="name"]//a/text()')
            loader.add_xpath('price', './/p[@class="price"]/text()')
            yield loader.load_item()

