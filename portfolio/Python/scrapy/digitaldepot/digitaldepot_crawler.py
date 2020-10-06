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

class DigitalDepotSpider(BaseSpider):
    name = 'digitaldepot.co.uk'
    allowed_domains = ['www.digitaldepot.co.uk', 'digitaldepot.co.uk']
    start_urls = ('http://www.digitaldepot.co.uk/catalog/seo_sitemap/category/',)

    def __init__(self, *args, **kwargs):
        super(DigitalDepotSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//div[@class="content"]/ul[@class="bare-list"]//a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)


        # pagination
        next_page = hxs.select(u'//a[child::img[@alt="Next" or @title="Next"]]/@href').extract()
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
        products = hxs.select('//div[@class="f-fix"]')

        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            url = product.select(u'.//h2/a/@href').extract()[0]
            url = urljoin_rfc(get_base_url(response), url)
            product_loader.add_value('url', url)
            product_loader.add_xpath('name', u'.//h2/a/text()')
            product_loader.add_xpath('price', u'.//span[contains(@id,"product-price")]/span[@class="price"]/text()',
                                             re=u'\xa3(.*)')
            product_loader.add_xpath('price', u'.//span[contains(@id,"product-price") and @class="price"]/text()',
                                             re=u'\xa3(.*)')
            yield product_loader.load_item()