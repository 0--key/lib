import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

from scrapy import log

class ThePerfumeSpotSpider(BaseSpider):
    name = 'theperfumespot.com'
    allowed_domains = ['theperfumespot.com']
    start_urls = ('http://www.theperfumespot.com/',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        categories = hxs.select('//div[@class="catNav"]//ul/li/div/a/@href').extract()

        for cat in categories:
            yield Request(urljoin_rfc(get_base_url(response), cat), callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)

        products = hxs.select('//div[@class="contentsName"]/..')

        for p in products:
            url = p.select('.//div[@class="contentsName"]//a/@href').extract()[0]
            if not p.select('.//div[@class="contentsSalePrice"]'):
                yield Request(urljoin_rfc(get_base_url(response), url), callback=self.parse_products)
            else:
                loader = ProductLoader(item=Product(), selector=p)
                loader.add_value('url', urljoin_rfc(get_base_url(response), url))
                loader.add_xpath('name', './/div[@class="contentsName"]//a/text()')
                loader.add_xpath('price', './/div[@class="contentsSalePrice"]/font/text()')
                loader.add_value('sku', url.split('-')[-1].replace('.html', ''))

                yield loader.load_item()