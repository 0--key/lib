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

class Belowtradeprices(BaseSpider):
    name = 'belowtradeprices.co.uk'
    allowed_domains = ['www.belowtradeprices.co.uk', 'belowtradeprices.co.uk']

    def start_requests(self):
        start_urls = ('http://www.belowtradeprices.co.uk',
                      'http://www.belowtradeprices.co.uk/domestic.aspx',
                      'http://www.belowtradeprices.co.uk/office-furniture.aspx')
        yield Request(start_urls[0], meta={'exvat': True})
        for url in start_urls[1:]:
            yield Request(url, meta={'exvat': False})

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//div[@class="Category"]//a/@href').extract()
        categories += hxs.select(u'//h3[@class="Org LeftNavMenu"]//a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, meta=response.meta)

        # pagination
        next_page = hxs.select(u'//div[@class="pager"]//a[contains(text(),"Next")]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            if next_page.count(u'&page=') > 1:
                next_page = re.sub(u'&page=\d+', u'', next_page, 1)
            yield Request(next_page, meta=response.meta)

        # products
        products = hxs.select(u'//div[contains(@class,"ProDes1")]/div/a/@href').extract()
        for url in products:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product, meta=response.meta)

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        loader = ProductLoader(item=Product(), response=response)
        name = hxs.select('//span[@id="ContentPlaceHolder1_lblproductame"]/text()').extract()[0]
        #sku = hxs.select(u'//div[@id="product-price"]/span[contains(text(),"Model Number")]/text()').extract()[0]\
        #        .replace('\n', '')
        #sku = re.search(u'Model Number:(.*)', sku).groups()[0].strip()
        sku = hxs.select('//h3/text()').extract()[0].strip()
        loader.add_value('url', response.url)
        loader.add_value('name', name)
        loader.add_value('sku', sku)
        if response.meta.get('exvat', False):
            loader.add_xpath('price', u'//div[@id="MainInner"]//span[@class="Price1"]/span/text()')
        else:
            loader.add_xpath('price', u'//div[@id="product-price"]//span[contains(@id,"lblVat")]/text()')
        if loader.get_output_value('price'):
            yield loader.load_item()
