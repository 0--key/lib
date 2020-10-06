import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

import csv

from product_spiders.items import Product, ProductLoader


class HughesDirectSpider(BaseSpider):
    name = 'hughesdirect.co.uk'
    allowed_domains = ['www.hughesdirect.co.uk', 'hughesdirect.co.uk']
    start_urls = ('http://hughesdirect.co.uk/',)

    def __init__(self, *args, **kwargs):
        super(HughesDirectSpider, self).__init__(*args, **kwargs)
        self.monitored_categories = (u'VISION', u'HIFISYSTEMS', u'PORTABLEHIFI', u'ACCESSORIES')

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = []
        for monitored_category in self.monitored_categories:
            categories += hxs.select(u'//li[child::a[contains(@class,"' + monitored_category + '")]]//ul//a/@href').extract()
        for url in categories:
            url = url.split('/')
            url = '/'.join(url[:-1] + ['all'] + url[-1:])
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_category,
                          cookies={}, meta={'dont_merge_cookies': True})

    def parse_category(self, response):
        # pages
        hxs = HtmlXPathSelector(response)
        show_all = hxs.select(u'//a[contains(text(),"Show All")]/@href').extract()
        if show_all:
            yield Request(response.url, callback=self.parse_category, dont_filter=True,
                          cookies={}, meta={'dont_merge_cookies': True})
        else:
            for product in self.parse_product(response):
                yield product

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)


        products = hxs.select('//ul[@class="product-list"]/li')
        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)

            name = product.select('.//h2/a/strong/text()').extract()[0]
            extra_name = product.select('.//h2/a/text()').extract()
            if extra_name:
                name += ' ' + extra_name[0]
            product_loader.add_value('name', name)
            url = product.select('.//h2/a/@href').extract()
            url = urljoin_rfc(get_base_url(response), url[0])
            product_loader.add_value('url', url)
            product_loader.add_xpath('price', u'.//p/strong/text()', re='\xa3(.*)')
            yield product_loader.load_item()

        if not products and not response.meta.get('retry'):
            yield Request(response.url, callback=self.parse_product, dont_filter=True,
                          cookies={}, meta={'dont_merge_cookies': True, 'retry': True})
