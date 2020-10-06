import re
import logging

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class LaudiusNlSpider(BaseSpider):
    name = 'laudius.nl'
    allowed_domains = ['laudius.nl']
    start_urls = ('http://www.laudius.nl',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//div[@class="menu"]/ul/li[@class="title"]/a/@href').extract():
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_course_list)

    def parse_course_list(self, response):
        hxs = HtmlXPathSelector(response)

        url_list = hxs.select(u'//div[@class="tx-ppw-courses"]//a/@href').extract()
        for url in url_list:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_course)

    def parse_course(self, response):
        hxs = HtmlXPathSelector(response)

        path = hxs.select(u'//div[@class="breadcrumb"]/span/a/text()').extract()
        path.extend(hxs.select(u'//h1[@class="course"]/text()').extract())

        price = hxs.select(u'//div[contains(@class,"registration")]//td[contains(text(),"1x")]/text()').extract()
        # This happens on link to comparison of all courses
        if not price:
            return
        price = price[0].replace('1x', '').replace(u'\u20ac', '').replace('.', '').replace(',', '.')

        product_loader = ProductLoader(item=Product(), selector=hxs)
        product_loader.add_value('name', u' / '.join(path))
        product_loader.add_value('url', response.url)
        product_loader.add_value('price', price)
        yield product_loader.load_item()
