from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class SoundsliveSpider(BaseSpider):
    name = 'soundslive.co.uk'
    allowed_domains = ['soundslive.co.uk']
    start_urls = ['http://www.soundslive.co.uk']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        relative_urls = hxs.select('//tr[@class="Menu2"]/td/a/@href').extract()
        for relative_url in relative_urls:
            url = urljoin_rfc('http://www.soundslive.co.uk',
                              relative_url, response.encoding)

            yield Request(url, callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//tr[@class="Item1" or @class="Item2"]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', 'td[@width="69%"]/a/text()')
            relative_url = product.select('td[@width="69%"]/a/@href').extract()[0]
            url = urljoin_rfc('http://www.soundslive.co.uk', 
                              relative_url, response.encoding)
            loader.add_value('url', url)
            price = 0.0
            if product.select('td[@width="15%"]/b/text()'):
                price = product.select('td[@width="15%"]/b/text()').extract()[0] 
            loader.add_value('price', price)
            yield loader.load_item()
