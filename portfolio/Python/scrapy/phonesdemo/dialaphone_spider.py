from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class DialaphoneSpider(BaseSpider):
    name = 'dialaphone.co.uk'
    allowed_domains = ['dialaphone.co.uk']
    start_urls = ['http://www.dialaphone.co.uk/pay-as-you-go/']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        urls = hxs.select('//*[@id="ulManufacturerLinks"]/li/a/@href').extract()
        for url in urls:
            yield Request(url, callback=self.parse_categories)

    def parse_categories(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//table[@class="List"]/tr')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', 'td[@class="DealIncludes"]/a[@class="PhoneName"]/text()')
            loader.add_xpath('url', 'td[@class="DealIncludes"]/a[@class="PhoneName"]/@href')
            price = 0.0
            if product.select('td[@class="Price"]/text()'):
                price = product.select('td[@class="Price"]/text()').extract()[0]
            loader.add_value('price', price)
            yield loader.load_item()
