from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class GoOutdoorsSpider(BaseSpider):
    name = 'gooutdoors.co.uk'
    allowed_domains = ['gooutdoors.co.uk']
    start_urls = ['http://www.gooutdoors.co.uk/camping/tents/']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        relative_urls = hxs.select('//*[@id="catNav"]/ul/li/ul/li/a/@href').extract()
        for relative_url in relative_urls:
            url = urljoin_rfc('http://www.gooutdoors.co.uk/',
                              relative_url,
                              response.encoding)

            yield Request(url, callback=self.parse_categories)

    def parse_categories(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="in"]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            relative_url = product.select('h3/a/@href').extract()[0]
            loader.add_value('url', urljoin_rfc('http://www.gooutdoors.co.uk/',
                                                relative_url, 
                                                response.encoding))
            loader.add_xpath('name', 'h3/a/text()')
            loader.add_xpath('price', 'div[@class="price"]/text()')
            yield loader.load_item()
        next_page = hxs.select('//*[@id="pSrchFtr"]/div/span/a/@href').extract()
        if next_page:
            url = urljoin_rfc('http://www.gooutdoors.co.uk/', 
                              next_page[0], 
                              response.encoding)
            yield Request(url, callback=self.parse_categories)
