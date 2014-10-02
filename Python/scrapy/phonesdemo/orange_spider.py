from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class OrangeSpider(BaseSpider):
    name = 'orange.co.uk'
    allowed_domains = ['shop.orange.co.uk']
    start_urls = ['http://shop.orange.co.uk/mobile-phones/pay-as-you-go']

    def parse(self, response):
        BASE_URL = 'http://shop.orange.co.uk/'
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="phone-details"]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', 'div[@class="phone-name"]/a/h4/text()')
            relative_url = product.select('div[@class="phone-name"]/a/@href').extract()[0]
            url = urljoin_rfc(BASE_URL, relative_url, response.encoding)
            loader.add_value('url', url)
            loader.add_xpath('price', 'div[@class="channel-prices PAYGAc"]/em/text()')
            yield loader.load_item()
