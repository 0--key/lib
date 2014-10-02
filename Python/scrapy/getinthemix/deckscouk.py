import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest

class DecksCoUk(BaseSpider):
    name = 'decks.co.uk'
    allowed_domains = ['decks.co.uk', 'www.decks.co.uk']
    start_urls = ('http://www.decks.co.uk',)

    def parse_product(self, response):
        URL_BASE = 'http://www.decks.co.uk'

        hxs = HtmlXPathSelector(response)
        
        products = hxs.select('//div[@id="search-results"]/ul/li')
        for p in products:
            res = {}
            name = p.select('.//h2/a/text()')[0].extract()
            url = p.select('.//h2/a/@href')[0].extract()
            url = urljoin_rfc(URL_BASE, url)
            price = p.select('.//h3[@class="price"]/strong/text()').re('\xa3(.*)')[0]
            res['url'] = url
            res['description'] = name
            res['price'] = price
            yield load_product(res, response)


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        
        URL_BASE = 'http://www.decks.co.uk'
        #categories
        hxs = HtmlXPathSelector(response)
        #category_urls = hxs.select('//div[@class="products-nav"]/ul/li/a/@href').extract()
        category_urls = hxs.select('//div[starts-with(@class,"radnav")]//a/@href').extract()
        for url in category_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        #subcategories (for categories that don't show the products directly)
        subcategories_urls = hxs.select('//ul[@class="smaller"]//p[@class="go"]/a/@href').extract()
        for url in subcategories_urls:
           url = urljoin_rfc(URL_BASE, url)
           yield Request(url)

        # products
        products = [p for p in self.parse_product(response)]
        for p in products:
            yield p

        #next page
        next_page = hxs.select('//a[contains(text(),"Next")]/@href').extract()
        if next_page and products:
            url = urljoin_rfc(URL_BASE, next_page[0])
            yield Request(url)

