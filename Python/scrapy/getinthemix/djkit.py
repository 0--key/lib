import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest

class DjKit(BaseSpider):
    name = 'djkit.com'
    allowed_domains = ['djkit.com', 'www.djkit.com']
    start_urls = ('http://www.djkit.com',)

    def parse_product(self, response):
        URL_BASE = 'http://www.djkit.com'

        hxs = HtmlXPathSelector(response)
        
        products = hxs.select('//a[@class="product"]/../..')
        for p in products:
            res = {}
            name = p.select('.//div[@class="title"]/a/text()')[0].extract()
            url = p.select('..//div[@class="title"]/a/@href')[0].extract()
            url = urljoin_rfc(URL_BASE, url)
            price = p.select('.//div[@class="showprice"]/span/text()').re('.(.*)')[0]
            res['url'] = url
            res['description'] = name
            res['price'] = price
            yield load_product(res, response)


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        URL_BASE = 'http://www.djkit.com'
        #categories
        hxs = HtmlXPathSelector(response)
        category_values = hxs.select('//select[@name="manufacturer"]//option/@value').extract()
        for value in category_values:
            if value == '0':
                continue
            url = URL_BASE + '/search.php?manufacturer=' + value
            yield Request(url)

        #next page
        next_pages = hxs.select('//div[@class="page"]')
        if next_pages:
            next_pages = next_pages[0].select('./a/@href') #use the first paginator
            for page in next_pages.extract():
                url = urljoin_rfc(URL_BASE, page)
            yield Request(url)

        # products
        for p in self.parse_product(response):
            yield p
