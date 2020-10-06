import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

import csv

from product_spiders.items import Product, ProductLoader


class SevenOaksSpider(BaseSpider):
    name = 'sevenoakssoundandvision.co.uk'
    allowed_domains = ['www.store.sevenoakssoundandvision.co.uk', 'store.sevenoakssoundandvision.co.uk',
                       'sevenoakssoundandvision.co.uk']
    start_urls = ('http://store.sevenoakssoundandvision.co.uk/products/category/1765.0.4.3.45962.0.0.0.0',)

    def __init__(self, *args, **kwargs):
        super(SevenOaksSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//td[@class="sub_category"]//a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pages
        next_pages = hxs.select(u'//a[contains(text(),"Next")]/@href').extract()
        for next_page in next_pages:
            url = urljoin_rfc(get_base_url(response), next_page)
            yield Request(url)

        # products
        
        for product in self.parse_product(response):
            yield product


    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)


        products = hxs.select(u'//div[@id="list_block"]')
        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)

            name = product.select(u'.//h2/a/text()').extract()[0]
            extra_name = hxs.select('.//h2/a/p/text()').extract()
            if extra_name:
                name += ' ' + extra_name[0]
            product_loader.add_value('name', name)
            url = product.select('.//h2/a/@href').extract()
            url = urljoin_rfc(get_base_url(response), url[0])
            product_loader.add_value('url', url)
            product_loader.add_xpath('price', u'.//td[@class="list_price"]/h3/text()', re='\xa3 (.*)')
            yield product_loader.load_item()
