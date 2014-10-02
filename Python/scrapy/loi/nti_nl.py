import re
import logging

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class NtiNlSpider(BaseSpider):
    name = 'nti.nl'
    allowed_domains = ['nti.nl']
    start_urls = ('http://www.nti.nl',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//div[@id="header"]//ul[@class="menu"]/li/a/@href').extract():
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_field)

    def parse_field(self, response):
        hxs = HtmlXPathSelector(response)

        # The same course falls into multiple categories
        # collect all categories before yielding courses
        fields = []
        courses = {}
        for field in hxs.select(u'//ul[@class="Facets"]/li/a'):
            # Remove number of courses from field name "Foobar (13)"
            field_name = field.select(u'text()').extract()[0].split(' (')[0].strip()
            field_url = field.select(u'@href').extract()[0]
            field_url = urljoin_rfc(get_base_url(response), field_url)
            fields.append((field_name, field_url))

        if fields:
            field_name, field_url = fields.pop()
            yield Request(field_url, meta={
                    'fields': fields,
                    'courses': courses,
                    'field_name': field_name,
                    }, callback=self.parse_course_list)

    def parse_course_list(self, response):
        hxs = HtmlXPathSelector(response)

        programs = hxs.select(u'//ul[@id="SearchResults"]/li/h2/a/@href').extract()
        if programs:
            for url in programs:
                url = urljoin_rfc(get_base_url(response), url)
                response.meta['courses'].setdefault(url, []).append(response.meta['field_name'])
        else:
            response.meta['field_names'] = [response.meta['field_name']]
            for x in self.parse_course(response):
                yield x

        # Pagination
        next_url = hxs.select(u'//div[@id="PageNumbers"]/a[@class="next"]/@href').extract()
        if next_url:
            url = urljoin_rfc(get_base_url(response), next_url[0])
            yield Request(url, meta=response.meta, callback=self.parse_course_list)
        # Next field
        elif response.meta['fields']:
            field_name, field_url = response.meta['fields'].pop()
            response.meta['field_name'] = field_name
            yield Request(field_url, meta=response.meta, callback=self.parse_course_list)
        # All fields processed, do courses
        else:
            for course, fields in response.meta['courses'].items():
                yield Request(course, meta={'field_names': fields}, callback=self.parse_course)

    def parse_course(self, response):
        hxs = HtmlXPathSelector(response)
        durations = hxs.select(u'//tr/th/text()').extract()
        prices = hxs.select(u'//tr/td[starts-with(text(),"\u20ac")]/../td/text()').extract()
        price = None

        def get_price(i):
            return float(durations[i].split()[0]) * float(prices[i].replace(u'\u20ac', '').replace('.', '').replace(',', '.'))

        for i, duration in enumerate(durations):
            # Should pick the one with asterix
            if '*' in duration:
                price = get_price(i)

        # If no price with asterix found, take any
        if not price and prices:
            price = get_price(len(durations) - 1)

        if not price:
            logging.error("No price found at URL [%s]" % (response.url))
            return
                
        path = hxs.select(u'//div[@class="breadcrumbs"]/a/text()').extract()
        # XXX add field to name
        fields = response.meta['field_names']
        fields.sort()
        path.append(', '.join(fields))
        # Course name is without URL
        path.extend(hxs.select(u'//div[@class="breadcrumbs"]/em/text()').extract())
        # remove Home
        path.pop(0)

        product_loader = ProductLoader(item=Product(), selector=hxs)
        product_loader.add_value('name', u' / '.join(path))
        product_loader.add_value('url', response.url)
        product_loader.add_value('price', price)
        yield product_loader.load_item()
