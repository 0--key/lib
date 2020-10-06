import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product
from productloader import WindowsCleaningProductLoader

class JracensteinSpider(BaseSpider):
    name = 'jracenstein.com'
    allowed_domains = ['www.jracenstein.com']
    start_urls = ('http://www.jracenstein.com/store/index.asp',)

    def parse(self, response):
        BASE = 'http://www.jracenstein.com'
        #categories
        hxs = HtmlXPathSelector(response)
        #category_urls = hxs.select('//a/@href').re('(.*items.asp.*)')
        category_urls = hxs.select('//div[@class="pageBodyLeft"]/ul[1]//a/@href').extract()
        category_urls += hxs.select('//div[@class="categoryItem"]//h1/a/@href').extract()
        for url in category_urls:
            url = urljoin_rfc(BASE, url)
            yield Request(url)

        product_links = hxs.select('//div[starts-with(@id, "item")]//a/@href').extract()
        for link in product_links:
            link = urljoin_rfc(BASE, link)
            yield Request(link, callback=self.parse_product)


    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        # sub products
        hxs = HtmlXPathSelector(response)

        product = Product()
        loader = WindowsCleaningProductLoader(item=product, response=response)
        try:
            loader.add_value('url', response.url)
            name = hxs.select('//div[@class="bigbox"]/div[@class="top"]/text()').extract()[0]
            loader.add_value('name', name)
            price = hxs.select('//div[@class="priceAmount"]/text()').extract()[0]
            loader.add_value('price', price)
            try:
                sku = hxs.select('//font[@class="content" and contains(text(), "Model")]/../../td[2]/font/text()').extract()[0]
            except IndexError:
                sku = ''

            loader.add_value('sku', sku)

            yield loader.load_item()
        except IndexError:
            return
  
