import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode

import csv

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class PharmaPacksSpider(BaseSpider):
    name = 'pharmapacks.com'
    allowed_domains = ['www.pharmapacks.com', 'pharmapacks.com']
    start_urls = ('http://pharmapacks.com/',)

    def __init__(self, *args, **kwargs):
        super(PharmaPacksSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
                    return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//div[@id="Menu"]/ul/li/a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pages
        next_page = hxs.select(u'//div[@class="CategoryPagination"]//a[contains(text(),"Next")]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(next_page)

        # products
        for product in self.parse_product(response):
            yield product

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)
        products = hxs.select(u'//form[@name="frmCompare"]//ul[@class="ProductList "]//li')

        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            url = product.select(u'.//div[@class="ProductDetails"]/strong/a/@href').extract()[0]
            url = urljoin_rfc(get_base_url(response), url)
            product_loader.add_value('url', url)
            product_loader.add_xpath('name', u'.//div[@class="ProductDetails"]/strong/a/text()')
            product_loader.add_xpath('price', u'.//div[@class="ProductPriceRating"]/em/text()',
                                 re=u'\$(.*)')
            yield product_loader.load_item()