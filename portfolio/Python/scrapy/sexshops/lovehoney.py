import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product	

from scrapy.http import FormRequest

class LoveHoney(BaseSpider):
    name = 'lovehoney.co.uk'
    allowed_domains = ['lovehoney.co.uk', 'www.lovehoney.co.uk']
    start_urls = ('http://www.lovehoney.co.uk',)
    
    def __init__(self, *args, **kwargs):
        super(LoveHoney, self).__init__(*args, **kwargs)
        self.URL_BASE = 'http://www.lovehoney.co.uk'
        
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        res = {}
        try:
            name = hxs.select('//div[@id="product-detail"]/h1/text()').extract()[0]
            url = response.url
            price = hxs.select('//div[@id="product-detail"]/p[@class="ours"]/strong/text()').re('\xa3(.*)')[0]
            res['url'] = url
            res['description'] = name
            res['price'] = price
            res['sku'] = ''
            yield load_product(res, response)
        except IndexError:
            return


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)
        # categories
        # enter only from the main page
        if response.url == self.URL_BASE:
            #categories = hxs.select('//div[@id="col-left"]//a/@href').extract()
            categories = hxs.select('//div[@id="pNav"]//li[starts-with(@id, "pn")]//a/@href').extract()
            for url in categories:
                url = urljoin_rfc(self.URL_BASE, url)
                yield Request(url)

        # subcategories
        #subcategories = hxs.select('//ul/li[contains(text(), "Category")]//a/@href').extract()
        #for url in subcategories:
         #       url = urljoin_rfc(self.URL_BASE, url)
          #      yield Request(url)

        # next page
        next_page = hxs.select('//div[@class="pagination"]//a[contains(text(),"Next")]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(self.URL_BASE, next_page[0])
            yield Request(next_page)

        # products
        #products = hxs.select('//div[contains(@class,"chunk")]')
        products = hxs.select('//h4/a[contains(@href, "product.cfm")]/..')
        for product in products:
            try:
                url = product.select('.//a/@href').extract()[0]
                url = urljoin_rfc(self.URL_BASE, url)
                yield Request(url, callback=self.parse_product)
            except IndexError:
                continue
