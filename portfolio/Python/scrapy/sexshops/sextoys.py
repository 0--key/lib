import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product

from scrapy.http import FormRequest

class SexToys(BaseSpider):
    name = 'sextoys.co.uk'
    allowed_domains = ['sextoys.co.uk', 'www.sextoys.co.uk']
    start_urls = ('http://www.sextoys.co.uk',)
    
    def __init__(self, *args, **kwargs):
        super(SexToys, self).__init__(*args, **kwargs)
        self.URL_BASE = 'http://www.sextoys.co.uk'
        
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)
        res = {}
        try:
            name = hxs.select('//a[@class="url"]/text()').extract()[0]
            url = response.url
            price = hxs.select('//div[@class="viewpageourprice"]/span/text()').extract()
            if not price:
                price = hxs.select('//select[@class="productpage_viewpagesubbox"]/option/text()').re('\xa3(.*)')
            sku = hxs.select('//span[@class="sku"]/text()').extract()[0]
            res['url'] = url
            res['description'] = name
            res['price'] = price[0]
            res['sku'] = sku
            yield load_product(res, response)
        except IndexError:
            return


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)
        # categories
        categories = hxs.select('//div[@id="MainMenubar"]/ul/li/a/@href')[:-3].extract() # ignore the last three categories
        categories += hxs.select('//div[@id="MainMenu"]//a[contains(@class, "addarrow")]/@href').extract()
        for url in categories:
            url = urljoin_rfc(self.URL_BASE, url)
            yield Request(url)

        # next page
        next_page = hxs.select('//span[@class="navgonext"]/a/@href').extract()
        if next_page:
            next_page = urljoin_rfc(self.URL_BASE, next_page[0])
            yield Request(next_page)

        # products
        products = hxs.select('//div[@class="prod_productname"]//h5/a/@href').extract()
        for product in products:
            product = urljoin_rfc(self.URL_BASE, product)
            yield Request(product, callback=self.parse_product)
