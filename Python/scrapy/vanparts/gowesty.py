import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

import csv

from product_spiders.items import Product, ProductLoader


class GoWestySpider(BaseSpider):
    name = 'gowesty.com'
    allowed_domains = ['www.gowesty.com']
    start_urls = ('http://www.gowesty.com/',)

    def __init__(self, *args, **kwargs):
        super(GoWestySpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        if response.url == 'http://www.gowesty.com/' or response.url == 'http://www.gowesty.com':
            # ignore the first ten categories.
            categories = hxs.select('//div[@class="box_content"]/div[@id="categories"]//a/@href').extract()[11:]
            for url in categories:
                url = urljoin_rfc(get_base_url(response), url)
                yield Request(url)
            
        # pages
        next_page = hxs.select('//a/strong[contains(text(),"Next")]/../@href').extract()
        if next_page:
            sys.exit(0)
            url = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(url)

        # products
        for product in self.parse_product(response):
            yield product


    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        # products
        products = hxs.select('//div[@class="product_listing"]')

        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            #product_loader.add_xpath('name', './/span[@class="prod_name"]/a/@title')
            product_loader.add_xpath('price', './/span[@class="prod_our_price"]/strong/text()',
                                     re='.*\$(.*[0-9])')
            sku = product.select('.//span[@class="prod_number"]/text()').re('\((.*)\)')
            sku = re.sub('[\-]', '', sku[0])
            product_loader.add_value('sku', sku)
            if sku:
                product_loader.add_value('name', sku.lower())
            else:
                product_loader.add_xpath('name', './/span[@class="prod_name"]/a/@title')
            url = product.select('.//span[@class="prod_name"]/a/@href').extract()
            url = urljoin_rfc(get_base_url(response), url[0])
            product_loader.add_value('url', url)
            yield product_loader.load_item()