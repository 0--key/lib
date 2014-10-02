from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class GakSpider(BaseSpider):
    name = 'gak.co.uk'
    allowed_domains = ['gak.co.uk']
    start_urls = ['http://www.gak.co.uk/']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        relative_urls = hxs.select('//div[@class="tabs_menu"]/ul/li/a/@href').extract()
        for relative_url in relative_urls:
            url = urljoin_rfc('http://www.gak.co.uk/',
                              relative_url, response.encoding)

            yield Request(url, callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="snapshot"]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', 'div/a/text()')
            relative_url = product.select('div[@class="dsc"]/a/@href').extract()[0]
            url = urljoin_rfc('http://www.gak.co.uk/', 
                              relative_url, response.encoding)
            loader.add_value('url', url)
            price = 0.0
            if product.select('div/div/span/text()'):
                price = product.select('div/div/span/text()').extract()[0]
            loader.add_value('price', price)
            yield loader.load_item()

      
