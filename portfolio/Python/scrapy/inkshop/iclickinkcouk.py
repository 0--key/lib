import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc


from scrapy.http import FormRequest
from productloader import load_product

class IClickInk(BaseSpider):
    name = 'iclickink.co.uk'
    allowed_domains = ['iclickink.co.uk', 'www.iclickink.co.uk']
    start_urls = ('http://www.iclickink.co.uk',)
    
    def __init__(self, *args, **kwargs):
        super(IClickInk, self).__init__(*args, **kwargs)
        self.URL_BASE = 'http://www.iclickink.co.uk'
        
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        products = hxs.select('//table[@class="product_list"]//tr[not(@class)]')
        for product in products:
            res = {}
            try:
                name = product.select('.//a[@href!="#"]/text()').extract()[0]
                url = product.select('.//a[@href!="#"]/@href').extract()[0]
                url = urljoin_rfc(self.URL_BASE, url)
                price = product.select('.//div[@class="AXISBreakPricing1"]/div[@class="AXISBreakPricingPrice"]').re('\xa3(.*?)<')[0]
                res['url'] = url
                res['description'] = name
                res['price'] = price
                res['sku'] = res['description']
                yield load_product(res, response)
            except IndexError:
                continue


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)
        # categories
        #categories = hxs.select('//div[@class="brands"]/ul/li/a/@href').extract()
        categories = hxs.select('//div[@class="grid_16"]/ul/li/a/@href').extract()
        for url in categories:
            url = urljoin_rfc(self.URL_BASE, url)
            yield Request(url)
        # printers models
        printers_list = hxs.select('//div[contains(@class,"items")]//a/@href').extract()
        for url in printers_list:
            url = urljoin_rfc(self.URL_BASE, url)
            yield Request(url)


        # next page
        next_page = hxs.select('//a[@class="AXISPageNumber" and contains(text(),"Next")]/@href').extract()
        if next_page:
            url = urljoin_rfc(self.URL_BASE, next_page[0])
            yield Request(url)

        # products
        for product in self.parse_product(response):
            yield product
