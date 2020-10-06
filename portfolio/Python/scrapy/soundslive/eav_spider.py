import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class EavSpider(BaseSpider):
    name = 'e-av.co.uk'
    allowed_domains = ['e-av.co.uk']
    start_urls = ['http://www.e-av.co.uk']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        urls = hxs.select('//*[@id="nav"]/li/a/@href').extract()
        for url in urls:
            yield Request(url, callback=self.parse_page)

    def parse_page(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//li[@class="item"]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', 'h5/a/text()')
            loader.add_xpath('url', 'h5/a/@href')
            #loader.add_xpath('price', 'div[@class="price-box"]/span[@class="regular-price"]/span/text()')
            xpath = 'div[@class="price-box"]/span[@class="regular-price"]/span[@class="price"]/text()'
            if product.select(xpath):
                price = product.select(xpath).extract()[0]
            else:
                xpath = 'div[@class="price-box"]/p[@class="special-price"]/span[@class="price"]/text()'
                if product.select(xpath):
                    price = product.select(xpath).extract()[0]
            #loader.add_xpath('price', 'div[@class="price-box"]/span[@class="special-price"]/span/text()')
            loader.add_value('price', price)
            yield loader.load_item()
        next_page = hxs.select('//div[@class="pages"]/ol/li/a[@title="Next"]/@href').extract()
        if next_page:
            next_url = next_page[-1]
            yield Request(next_url, callback=self.parse_page)

