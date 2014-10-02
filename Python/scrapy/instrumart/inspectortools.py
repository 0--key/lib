import re
import json

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.utils import extract_price

class InspectorToolsSpider(BaseSpider):
    name = 'inspectortools.com'
    allowed_domains = ['inspectortools.com']
    start_urls = ('http://www.inspectortools.com',
                  'http://www.inspectortools.com/http://www.inspectortools.com/Combustion-Analyzers-s/29.htm',
                  'http://www.inspectortools.com/Combustible-Gas-Leak-Detectors-s/47.htm',
                  'http://www.inspectortools.com/VOC-detectors-s/30.htm',
                  'http://www.inspectortools.com/Single-Gas-Detectors-s/33.htm',
                  'http://www.inspectortools.com/Multi-Gas-Detectors-s/31.htm',
                  'http://www.inspectortools.com/Carbon-Monoxide-Detectors-s/48.htm')

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        cats = []
        if response.url == self.start_urls[0]:
            cats += hxs.select('//div[@class="sidebar"]//a[not(@title="Shop By Manufacturer")]/@href').extract()

        for cat in cats:
            yield Request(urljoin_rfc(get_base_url(response), cat))

        for product in self.parse_products(hxs, response):
            yield product

    def parse_products(self, hxs, response):
        products = hxs.select('//table[@class="v65-productDisplay"]//a[contains(@class, "productnamecolor")]/..')
        if not products:
            products = hxs.select('//a[contains(@class, "productnamecolor")]/../..')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('url', './/a[contains(@class, "productnamecolor")]/@href')
            loader.add_xpath('name', './/a[contains(@class, "productnamecolor")]/text()')
            loader.add_xpath('price', './/font[contains(@class, "colors_productprice")]/text()')
            yield loader.load_item()
