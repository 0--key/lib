import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest

class DJStore(BaseSpider):#TODO Check products quantity (Pagination (?)).
    name = 'djstore.com'
    allowed_domains = ['djstore.com', 'www.djstore.com']
    start_urls = ('http://www.djstore.com',)

    def parse_product(self, response):

        URL_BASE = 'http://www.djstore.com'

        hxs = HtmlXPathSelector(response)
        
        products = hxs.select('//div[@class="fulllist"]//table')
        for p in products:
            res = {}
            name = p.select('.//a[@class="producttitle"]/text()')[0].extract()
            url = p.select('.//a[@class="producttitle"]/@href')[0].extract()
            price = p.select('.//span[@class="price"]/text()').re('\xa3(.*)')[0] #TODO Check price is the correct one.
            res['url'] = url
            res['description'] = name
            res['price'] = price
            yield load_product(res, response)


    def parse(self, response):
        URL_BASE = 'http://www.djstore.com'
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        #categories
        category_urls = hxs.select('//div[@id="leftbackground"]//a/@href').extract()
        for url in category_urls:
            yield Request(url)

        #next page
        next_page = hxs.select('//a[@title="next"]/@href').extract()
        if next_page:
            url = next_page[0]
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        # products
        for p in self.parse_product(response):
            yield p
