from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class ProductionRoomSpider(BaseSpider):
    name = 'production-room.com'
    allowed_domains = ['production-room.com']
    start_urls = ['http://www.production-room.com/top-brands.php']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        relative_urls = hxs.select('//*[@id="brand_list"]/li/a/@href').extract()
        for relative_url in relative_urls:
            url = urljoin_rfc('http://www.production-room.com/',
                              relative_url, response.encoding)

            yield Request(url, callback=self.parse_brands)

    
    def parse_brands(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//*[@id="products"]/ul[@class="product_list"]/li')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', 'div[@class="thumbnail"]/a/h4/text()')
            relative_url = product.select('div[@class="thumbnail"]/a/@href').extract()[0]
            url = urljoin_rfc('http://www.production-room.com/', 
                              relative_url, response.encoding)
            loader.add_value('url', url)
            price = ''
            if product.select('p/strong/text()').extract():
                price = product.select('p/strong/text()').extract()[0]
                if product.select('p/strong/span/text()').extract():
                    price += product.select('p/strong/span/text()').extract()[0]
            loader.add_value('price', price)
            yield loader.load_item()
        next_page = hxs.select('//ul[@class="subcategories pagination"]/li/a[text()="Next"]/@href').extract()
        if next_page:
            next_url = next_page[-1]
            url = urljoin_rfc('http://www.production-room.com/',
                               next_url, response.encoding)
            yield Request(url, callback=self.parse_brands)
