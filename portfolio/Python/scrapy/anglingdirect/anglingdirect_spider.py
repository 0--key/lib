import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

import csv

from product_spiders.items import Product, ProductLoader


class AnglingDirectSpider(BaseSpider):
    name = 'anglingdirect.co.uk'
    allowed_domains = ['www.anglingdirect.co.uk']
    start_urls = ('http://www.anglingdirect.co.uk/',)

    def __init__(self, *args, **kwargs):
        super(AnglingDirectSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//div[contains(@class,"drop-down-menu")]')[:-2]
        categories = categories.select(u'.//ul[@class="links-column "]//a/@href').extract()
        for url in categories:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        # pages
        next_page = hxs.select(u'//div[@class="paging"]//a[contains(text(),"Next")]/@href').extract()
        if next_page:
            url = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(url)

        # products
        products = hxs.select(u'//span[contains(@class,"product-box")]/a/@href').extract()
        for url in products:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product)


    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        multiple_options = hxs.select(u'//div[@id="spec-with-options"]//table//tr')[1:]

        name = hxs.select('//div[@id="product-title"]/text()').extract()[0]

        if not multiple_options:
            product_loader = ProductLoader(item=Product(), response=response)
            product_loader.add_value('name', name)
            product_loader.add_value('url', response.url)
            product_loader.add_xpath('price', u'//div[@class="price-now"]/span[contains(@id,"product-price")]/text()',
                                     re='\xa3(.*)')
            yield product_loader.load_item()
        else:
            for option in multiple_options:
                product_loader = ProductLoader(item=Product(), selector=option)
                option_name = option.select('./td[position()=2]/text()').extract()[0]
                product_loader.add_value('name', name + ' ' + option_name)
                product_loader.add_value('url', response.url)
                product_loader.add_xpath('price', './/div[@class="price-now"]/span/text()', re='\xa3(.*)')
                yield product_loader.load_item()