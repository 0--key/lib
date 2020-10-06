import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest

class GetInTheMix(BaseSpider):
    name = 'getinthemix.co.uk'
    allowed_domains = ['getinthemix.co.uk', 'www.getinthemix.co.uk']
    start_urls = ('http://www.getinthemix.co.uk',)

    def parse_product(self, response):
        URL_BASE = 'http://www.getinthemix.co.uk'
        
        hxs = HtmlXPathSelector(response)

        products = hxs.select('//div[contains(@class,"prod_item prod_grid")]')
        for p in products:
            res = {}
            name = p.select('.//div[@class="prod_title"]/a/@title')[0].extract()
            url = p.select('.//div[@class="prod_title"]/a/@href')[0].extract()
            url = urljoin_rfc(URL_BASE, url)
            price = p.select('.//div[@class="prod_price_web"]/text()')[0].extract()
            res['url'] = url
            res['description'] = name
            res['price'] = price
            yield load_product(res, response)


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        URL_BASE = 'http://www.getinthemix.co.uk'
        #categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//div[contains(@class,"brands_sub")]//a/@href').extract()
        for url in category_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)
            
        #subcategories
        subcategory_urls = hxs.select('//div[@class="cat_list"]//a/@href').extract()
        for url in subcategory_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)
        #next page
        next_pages = hxs.select('//div[@id="page_number"]//a/@href').extract()
        if next_pages:
            for page in next_pages:
                url = urljoin_rfc(URL_BASE, page)
                yield Request(url)

        # products
        for p in self.parse_product(response):
            yield p
