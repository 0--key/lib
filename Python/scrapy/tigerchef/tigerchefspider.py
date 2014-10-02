from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader


class TigerChefSpider(BaseSpider):
    name = 'tigerchef.com'
    allowed_domains = ['tigerchef.com']
    start_urls = ('http://www.tigerchef.com',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        #categories = hxs.select('//div[@class="sidebar_nav"]//li/a/@href').extract()

        categories = hxs.select('//div[@class="navigation"]/ul/li/a/@href').extract()
        categories += hxs.select('//ul[@class="cl_subs"]//a/@href').extract()
        loaded = False
        for category in categories:
            loaded = True
            yield Request(category)

        next_page = hxs.select('//a[@rel="next"]/@href').extract()
        if next_page:
            base_url = get_base_url(response)
            loaded = True
            yield Request(urljoin_rfc(base_url, next_page[0]))

        products = [product for product in self.parse_products(hxs)]
        for product in products:
            yield product

        if (not products or not loaded) and response.meta.get('retries', 0) < 3:
            yield Request(response.url, dont_filter=True,
                          meta={'retries': response.meta.get('retries', 0) + 1})


    def parse_products(self, hxs):
        products = hxs.select('//div[starts-with(@id, "product_")]')
        for product in products:
            product_loader = ProductLoader(Product(), product)
            product_loader.add_xpath('url', './/span[@class="description"]/a/@href')
            product_loader.add_xpath('name', './/span[@class="description"]/a/b/text()')
            #product_loader.add_xpath('price', './/label/text()')
            product_loader.add_xpath('price', './/div[@class="our_price"]/text()')
            product_loader.add_xpath('sku', './/span[@class="description"]', re='Model #:[\s(]*([\S^)]*)')
            yield product_loader.load_item()

