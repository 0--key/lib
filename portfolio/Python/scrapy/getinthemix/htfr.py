import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest

class HTFR(BaseSpider):
    name = 'htfr.com'
    allowed_domains = ['htfr.com', 'www.htfr.com']
    start_urls = ('http://www.htfr.com/c/229/dj_equipment',)

    def parse_product(self, response):

        URL_BASE = 'http://www.htfr.com'

        hxs = HtmlXPathSelector(response)
        
        products = hxs.select('//div[@class="productItem rectangle nocat"]')
        for p in products:
            res = {}
            name = ' '.join(p.select('.//h4/a/text()').extract())
            url = p.select('.//h4/a/@href')[0].extract()
            url = urljoin_rfc(URL_BASE, url)
            price = p.select('.//h5[@class="prodPrice"]/text()').re('\xa3(.*)')
            if not price:
                price = p.select('.//h5[@class="prodPrice"]/span/text()').re('\xa3(.*)')

            price = price[0]
            res['url'] = url
            res['description'] = name
            res['price'] = price
            yield load_product(res, response)


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        URL_BASE = 'http://www.htfr.com'

        hxs = HtmlXPathSelector(response)

        #next page
        next_page = hxs.select('//div[@class="paginationLinkNext"]/a/@href').extract()
        if next_page:
            url = urljoin_rfc(URL_BASE, next_page[0])
            yield Request(url)

        # products
        for p in self.parse_product(response):
            yield p
