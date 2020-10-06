import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode
import hashlib

import csv

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))

class HuntOfficeSpider(BaseSpider):
    name = 'huntoffice.ie'
    allowed_domains = ['www.huntoffice.ie', 'huntoffice.ie']
    start_urls = ('http://www.huntoffice.ie/site-directory.php',)

    def __init__(self, *args, **kwargs):
        super(HuntOfficeSpider, self).__init__(*args, **kwargs)
        self.skus = {}
        with open(os.path.join(HERE, 'officespot_skus.csv'), 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                self.skus[row[0]] = row[1]

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
                    return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//div[@id="page-holder"]/div[@class="all-col"]//ul//li//a/@href').extract()
        categories += hxs.select(u'//td[@class="category-cell"]//a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pagination
        next_page = hxs.select(u'//a[child::img[@alt="Next page"]]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(next_page)

        # products
        products = [url for url in hxs.select(u'//div[@id="gallery"]//h3/a/@href').extract() if 'javascript' not in url]
        products += hxs.select(u'//td[@class="product"]//h4/a/@href').extract()
        for url in products:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product)
    
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        product_loader = ProductLoader(item=Product(), response=response)
        product_loader.add_value('url', response.url)
        sku = hxs.select(u'//div[@class="product-desc"]/dl/dt[contains(text(),"Product Code")]/following-sibling::dd[1]/text()').extract()
        if sku:
            sku = sku[0].strip()
        if sku in self.skus:
            product_loader.add_value('sku', self.skus[sku])
        product_loader.add_xpath('name', u'//h1[@itemprop="name"]/text()')
        product_loader.add_xpath('price', u'//h3/strong[@class="price-1"]/text()',
                                  re=u'\u20ac(.*)')
        yield product_loader.load_item()