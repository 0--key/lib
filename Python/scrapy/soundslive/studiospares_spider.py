from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class ReidysSpider(BaseSpider):
    name = 'studiospares.com'
    allowed_domains = ['studiospares.com']
    start_urls = ['http://www.studiospares.com/']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        urls = hxs.select('//*[@id="catNav"]/li/a/@href').extract()
        for url in urls:
            yield Request(url, callback=self.parse_categories)

    def parse_categories(self, response):
        hxs = HtmlXPathSelector(response)
        urls = hxs.select('//*[@id="categorylist"]/ul[@class="categories"]/li/h2/a/@href').extract()
        for url in urls:
            yield Request(url, callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//*[@id="searchresults"]/div[@class="prods"]/ul/li')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', 'form/div/div[@class="details"]/h2/a/text()')
            loader.add_xpath('url', 'form/div/div[@class="details"]/h2/a/@href')
            loader.add_xpath('price', 'form/div/div[@class="details"]/div[@class="featprods_prices"]/p[@class="price"]/text()')
            yield loader.load_item()
        next_page = hxs.select('//span[@class="pagnNext"]/a/@href').extract()
        if next_page:
            next_url = next_page[-1]
            yield Request(next_url, callback=self.parse_products)

