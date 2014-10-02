
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector, XmlXPathSelector
from scrapy.http import Request
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url
from scrapy.utils.response import body_or_str
from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy import log
import re
from urlparse import urlparse, parse_qs


class MidLandWaterLifeSpider(BaseSpider):
    name = 'midlandwaterlife.com'
    allowed_domains = ['midlandwaterlife.com', 'www.midlandwaterlife.com']
    start_urls = ['http://www.midlandwaterlife.com/site_map.html']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//ul/li/a/@href').extract()
        for category in categories:
            url = urljoin_rfc(get_base_url(response), category)
            yield Request(url, callback=self.parse_category)

    def parse_one_for_page(self, response):
        log.msg("PARSE-ONE_FOR_PAGE FUNC")
        def get_prod(resp, hxs, price, desc=''):
            loader = ProductLoader(response=response, item=Product())
            loader.add_value('name', ''.join((name, desc)))
            loader.add_value('price', price)
            loader.add_value('url', url)
            return loader.load_item()

        hxs = HtmlXPathSelector(response)
        name = u''.join(hxs.select('//div[@class="back details_image"]/div'
                                  '//a/img/@title').extract()).split(u'\u00a3')[0]
        if 'from' in name:
            name = name.replace('from','')
        elif 'From' in name:
            name = name.replace('From', '')
        url = response.url
        prices = hxs.select('//div[@class="wrapperAttribsOptions"]'
                            '/div[@class="back"]/label/text()').extract()
        if not prices:
            prices = prices = hxs.select('//*[@id="productAttributes"]/div/'
                                         'div[@class="back"]/select/option/text()').extract()
        if prices:    
            for desc, price in [p.split(u'-') for p in prices if '-' in p]:
                yield get_prod(response, hxs, price, desc)
            price = ''.join(hxs.select('//span[@class="prod_price1"]/text()').extract()).strip()
            if price:
                desc = ''.join([p for p in prices if '-' not in p])
                if desc:
                    yield get_prod(response, hxs, price, desc)
        else:
            price = hxs.select('//span[@class="prod_price1"]/text()').extract()
            yield get_prod(response, hxs, price)

    def parse_category(self, response):
        hxs = HtmlXPathSelector(response)
        prods = hxs.select('//div[@class="centerBoxContentsProducts centeredContent back"]')
        if prods:
            for prod in prods:
                url = prod.select('.//div[@class="prod_name"]/a/@href').extract()[0]
                yield Request(url, callback=self.parse_one_for_page)
            next = hxs.select('//a[@title=" Next Page "]/@href').extract()
            if next:
                yield Request(next[-1], callback=self.parse_category)
        else:
            name = hxs.select('//div[@class="back details_image"]/div//a/img/@title').extract()
            if name:
                yield Request(response.url, dont_filter=True, callback=self.parse_one_for_page)

