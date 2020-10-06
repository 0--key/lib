import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from productloader import load_product


from scrapy.http import FormRequest

class StinkyInkShop(BaseSpider):
    name = 'stinkyinkshop.co.uk'
    allowed_domains = ['stinkyinkshop.co.uk', 'www.stinkyinkshop.co.uk']
    start_urls = ('http://www.stinkyinkshop.co.uk',)
    
    def __init__(self, *args, **kwargs):
        super(StinkyInkShop, self).__init__(*args, **kwargs)
        self.URL_BASE = 'http://www.stinkyinkshop.co.uk'
        
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        products = hxs.select('//article[starts-with(@class, "product")]')
        for p in products:
            res = {}
            name = p.select('.//span[@itemprop="ProductID"]/text()')[0].extract()
            url = p.select('.//h3/a/@href')[0].extract()
            url = urljoin_rfc(self.URL_BASE, url)
            price = p.select('.//span[@class="ex_vat"]/text()').re('\xa3(.*) ex')[0]
            res['url'] = url
            res['description'] = name
            res['price'] = price
            res['sku'] = res['description']
            yield load_product(res, response)


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        #categories
        hxs = HtmlXPathSelector(response)
        # printer brands
        printers_brands = hxs.select('//nav[@id="sidebar"]/ul/li/a/@href').extract()
        for url in printers_brands:
            url = urljoin_rfc(self.URL_BASE, url)
            yield Request(url)

        printers_series = hxs.select('//div[@class="thumbs"]//a[@class="button"]/@href').extract()
        for url in printers_series:
            url = urljoin_rfc(self.URL_BASE, url)
            yield Request(url)

        # printer list
        printers_list = hxs.select('//section[@class="printer-list"]//a/@href').extract()
        for url in printers_list:
            url = urljoin_rfc(self.URL_BASE, url)
            yield Request(url)

        # next page
        # next_page =
        # if next_page:
        #     url = urljoin_rfc(URL_BASE, next_page[0])
         #    yield Request(url)

        # products
        for p in self.parse_product(response):
            yield p
