import re
import json

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.utils import extract_price

class GlobalTestSupplySpider(BaseSpider):
    name = 'globaltestsupply.com'
    allowed_domains = ['globaltestsupply.com']
    start_urls = ('http://www.globaltestsupply.com',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        cats = []
        if response.url == self.start_urls[0]:
            cats += hxs.select('//div[@class="headermenubottom centar"]//a/@href').extract()

        for cat in cats:
            yield Request(urljoin_rfc(get_base_url(response), cat))

        for product in self.parse_products(hxs, response):
            yield product

    def parse_products(self, hxs, response):
        products = hxs.select('//table[@id="productCategoriesTable"]//tbody//tr')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', './/a/strong/text()')
            url = product.select('.//a/strong/../@href').extract()[0]
            loader.add_value('url', urljoin_rfc(get_base_url(response), url))
            if product.select('.//span[@class="red"]/strong/text()'):
                loader.add_xpath('price', './/span[@class="red"]/strong/text()')
            else:
                loader.add_value('price', '0')
            yield loader.load_item()

