import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

import csv

from product_spiders.items import Product, ProductLoader


class TackleUkSpider(BaseSpider):
    name = 'tackleuk.co.uk'
    allowed_domains = ['www.tackleuk.co.uk']
    start_urls = ('http://www.tackleuk.co.uk/',)

    def __init__(self, *args, **kwargs):
        super(TackleUkSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//td[@class="cat"]/a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pages
        # next_page = hxs.select(u'').extract()
        # if next_page:
        #     url = urljoin_rfc(get_base_url(response), next_page[0])
        #     yield Request(url)

        # products
        for product in self.parse_product(response):
            yield product


    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)
        
        products = hxs.select(u'//a[@class="main_desc"]/../../../../..')

        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            try:
                url = product.select(u'.//a[@class="href_products_name"]/@href').extract()[0]
                url += '#' + product.select(u'.//a[@class="href_products_name"]').re('onclick=\"dlh\(\\\'(.*)\\\'')[0]
            except IndexError:
                continue
            product_loader.add_value('url', url)
            product_loader.add_xpath('name', u'.//a[@class="href_products_name"]/text()')
            product_loader.add_xpath('price', u'.//span[@class="productSpecialPrice"]/b/font/text()', re=u'\xa3(.*)')
            product_loader.add_xpath('price', u'.//span[contains(@id,"price_")]/font/font/text()', re=u'\xa3(.*)')
            yield product_loader.load_item()