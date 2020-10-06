import re
import json

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.utils import extract_price

class MyFlukeStoreSpider(BaseSpider):
    name = 'myflukestore.com'
    allowed_domains = ['myflukestore.com']
    start_urls = ('http://www.myflukestore.com',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        cats = []
        if response.url == self.start_urls[0]:
            cats += hxs.select('//div[@class="navigation"]/ul/li[not(@class="home")]/a/@href').extract()

        next_pages = hxs.select('//span[@class="pages"]//a')
        for p in next_pages:
            if p.select('.//text()').re('\d+'):
                cats.append(p.select('.//@href').extract()[0])

        for cat in cats:
            yield Request(urljoin_rfc(get_base_url(response), cat))

        for product in self.parse_products(hxs, response):
            yield product

    def parse_products(self, hxs, response):
        products = hxs.select('//h3[@class="product_name"]/../..')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', './/h3[@class="product_name"]/a/text()')
            url = product.select('.//h3[@class="product_name"]/a/@href').extract()[0]
            url = urljoin_rfc(get_base_url(response), url)
            loader.add_value('url', url)
            loader.add_xpath('price', './/p[@class="price"]/text()')
            yield loader.load_item()
