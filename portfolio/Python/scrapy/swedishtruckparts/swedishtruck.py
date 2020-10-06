import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

import csv

from product_spiders.items import Product, ProductLoader


class SwedishTruckPartsSpider(BaseSpider):
    name = 'swedishtruckpartsshop.co.uk'
    allowed_domains = ['www.swedishtruckpartsshop.co.uk']
    start_urls = ('http://www.swedishtruckpartsshop.co.uk/',)

    def __init__(self, *args, **kwargs):
        super(SwedishTruckPartsSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select('//div[@class="rightcol"]//a[not(descendant::img)]/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pages
        # next_page = hxs.select('').extract()
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

        # products
        products = hxs.select(u'//div[@class="rightcol"]//td[contains(child::text(),"\xa3")] | //div[@class="rightcol"]//td[child::h1]')

        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            product_loader.add_xpath('name', './a/text()')
            product_loader.add_xpath('name', './h1/text()')
            url = product.select('./a/@href').extract()
            if not url:
                url = response.url
            else:
                url = urljoin_rfc(get_base_url(response), url[0])
            product_loader.add_value('url', url)
            price = product.select('./text()').re('\xa3(.*)')
            if not price:
                price = product.select('.//span[@id="_EKM_PRODUCTPRICE"]/text()').extract()
            if not price:
                continue
            product_loader.add_value('price', price)
            yield product_loader.load_item()