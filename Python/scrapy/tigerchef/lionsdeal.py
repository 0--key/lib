import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from product_spiders.utils import extract_price

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class LionsDealSpider(BaseSpider):
    name = 'lionsdeal.com'
    allowed_domains = ['lionsdeal.com']
    start_urls = ('http://www.lionsdeal.com',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        cats = hxs.select('//a[@class="c4subnav"]/@href').extract()
        cats += hxs.select('//table[@id="contents-table"]//div[@class="name"]/a/@href').extract()
        for cat in cats:
            yield Request(urljoin_rfc(get_base_url(response), cat))

        for product in self.parse_products(hxs, response):
            yield product

    def _get_sku(self, url):
        sku = url.split('/')[-1].replace('.html', '')
        if '-' in sku:
            sku = ''.join(sku.split('-', 1)[1:])

        return sku

    def parse_products(self, hxs, response):
        products = hxs.select('//div[starts-with(@id, "productData-")]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', './/a[@class="pagedLink"]/text()')
            loader.add_xpath('price', './/div[@class="pagedPriceSale"]/text()')
            url = product.select('.//a[@class="pagedLink"]/@href').extract()[0]
            loader.add_value('url', urljoin_rfc(get_base_url(response), url))
            sku = self._get_sku(url)
            loader.add_value('sku', sku)

            yield loader.load_item()

        products = hxs.select('//table[@id="multi"]//td[@id="multi-product3"]/..')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', './/td[position() = 2]/a/text()')
            url = product.select('.//td[position() = 2]/a/@href').extract()[0]
            loader.add_value('url', urljoin_rfc(get_base_url(response), url))
            loader.add_value('sku', self._get_sku(url))
            loader.add_xpath('price', './/td[@id="multi-price2"]//text()')
            yield loader.load_item()
