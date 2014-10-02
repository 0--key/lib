import re
import json

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.utils import extract_price

class TestEquitySpider(BaseSpider):
    name = 'testequity.com'
    allowed_domains = ['testequity.com']
    start_urls = ('http://www.testequity.com/categories/',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        cats = []
        if response.url == self.start_urls[0]:
            cats += hxs.select('//div[@id="categoryTree"]/ul/li/a[@class="CatPathLink"]/@href').extract()

        for cat in cats:
            yield Request(urljoin_rfc(get_base_url(response), cat))

        products = hxs.select('//td//img[contains(@src, "CartIcon.gif")]/../@href').extract()
        for product in products:
            yield Request(urljoin_rfc(get_base_url(response), product), callback=self.parse_product)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//td[@class="PriceColumn"]/..')
        for product in products:
            if product.select('.//td[@class="ItemAdCopy"]/b/a'):
                continue

            loader = ProductLoader(item=Product(), selector=product)
            name = product.select('.//td[@class="ItemAdCopy"]//text()').extract()[:3]
            name = name[1].strip() + ' ' + name[2].strip()

            loader.add_value('name', name)
            loader.add_xpath('price', './/td[@class="PriceColumn"]//text()')
            loader.add_value('url', response.url)
            yield loader.load_item()
