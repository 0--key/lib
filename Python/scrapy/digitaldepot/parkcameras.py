import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode

import csv

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class ParkCamerasSpider(BaseSpider):
    name = 'parkcameras.com'
    allowed_domains = ['www.parkcameras.com', 'parkcameras.com']
    start_urls = ('http://www.parkcameras.com/sitemap.aspx',)

    def __init__(self, *args, **kwargs):
        super(ParkCamerasSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//table[child::tr[@class="CategorySpecialsHead" and child::td[text()="Brands"]]]/tr[@class="CategorySpecialsItem"]//a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_pagination)

    def parse_pagination(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # pagination
        next_page = hxs.select(u'//div[@id="Paging"]//a[@id="TopPager_hlkNextPage"]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(next_page, callback=self.parse_pagination)

        # products
        products = hxs.select(u'//div[@class="listitem"]//div[@class="heading"]/a[child::span[@class="ProductListHead"]]/@href').extract()
        for url in products:
            yield Request(url, callback=self.parse_product)

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        product_loader = ProductLoader(item=Product(), response=response)
        product_loader.add_value('url', response.url)
        name = hxs.select(u'//h1[@class="product-title"]/text()').extract()
        if name:
            # replace the first space for the \xc2\xa0 symbol for compatibility with the names in the database
            name = name[0].strip().replace(u' ', '\xc2\xa0'.decode('utf-8'), 1)
            product_loader.add_value('name', name)
        product_loader.add_xpath('price', u'//span[@class="price"]/text()',
                                     re=u'\xa3(.*)')
        if product_loader.get_output_value('name'):
            yield product_loader.load_item()