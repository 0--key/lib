import re
import logging

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class NhaNlSpider(BaseSpider):
    name = 'nha.nl'
    allowed_domains = ['nha.nl']
    start_urls = ('http://www.nha.nl',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//div[@class="menucontent"]/ul/li/a/@href').extract():
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_sub)

    def parse_sub(self, response):
        hxs = HtmlXPathSelector(response)

        urls = hxs.select(u'//div[@class="contentoverview"]//h3/a/@href').extract()
        urls.extend(hxs.select(u'//div[contains(@class,"groupoverview")]/ul/li/a/@href').extract())
        for url in urls:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_course_list)

    def parse_course_list(self, response):
        hxs = HtmlXPathSelector(response)

        url_list = hxs.select(u'//div[@class="contentoverview"]//h3/a/@href').extract()
        if url_list:
            for url in url_list:
                url = urljoin_rfc(get_base_url(response), url)
                yield Request(url, callback=self.parse_course)
        else:
            for x in self.parse_course(response):
                yield x

    def parse_course(self, response):
        hxs = HtmlXPathSelector(response)

        price_names = hxs.select(u'//div[@class="priceblock"]//tr[1]/td/span/text()').extract()
        for course in hxs.select(u'//div[@class="priceblock"]//tr[position() > 1 and position() != last()]'):
            path = hxs.select(u'//div[@class="breadcrumbs"]/ul/li/a/text()').extract()
            #path.extend(hxs.select(u'//div[@class="breadcrumbs"]/ul/li[last()]/strong/text()').extract())
            path.extend(course.select(u'.//th/text()').extract())

            prices = course.select(u'.//td/strong/b/text()').extract()
            prices = [p.replace(u'\u20ac', '') for p in prices if u'\u20ac' in p]
            for i, price in enumerate(prices):
                name = path[:]
                if len(prices) > 1:
                    name[-1] = name[-1].strip() + ' (' + price_names[i].strip() + ')'
                product_loader = ProductLoader(item=Product(), selector=course)
                product_loader.add_value('name', u' / '.join((p.strip() for p in name)))
                product_loader.add_value('url', response.url)
                product_loader.add_value('price', price)
                yield product_loader.load_item()
