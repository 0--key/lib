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

class SRSMicrosystemsSpider(BaseSpider):
    name = 'srsmicrosystems.co.uk'
    allowed_domains = ['www.srsmicrosystems.co.uk', 'srsmicrosystems.co.uk']
    start_urls = ('http://www.srsmicrosystems.co.uk/sitemap.aspx',)

    def __init__(self, *args, **kwargs):
        super(SRSMicrosystemsSpider, self).__init__(*args, **kwargs)

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
        next_page = hxs.select(u'//div[@id="Paging"]/span[@class="right"]/a[@id="TopPager_hlkNextPage"]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(next_page, callback=self.parse_pagination)

        # products
        for product in self.parse_product(response):
            yield product

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)
        products = hxs.select(u'//div[@class="listitem"]')

        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            url = product.select(u'.//div[@class="heading"]/a[child::span[@class="ProductListHead"]]/@href').extract()[0]
            url = urljoin_rfc(get_base_url(response), url)
            product_loader.add_value('url', url)
            name = product.select(u'.//div[@class="heading"]/a/span[@class="ProductListHead"]/text()').extract()[0].strip()
            product_loader.add_value('name', name)
            product_loader.add_xpath('price', u'.//span[@class="price"]/span[@class="ProductListItem"]/text()',
                                             re=u'\xa3(.*)')
            yield product_loader.load_item()