from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class TmobilSpider(BaseSpider):
    name = 't-mobile.co.uk'
    allowed_domains = ['t-mobile.co.uk']
    start_urls = ['http://www.t-mobile.co.uk/shop/pay-as-you-go/mobile-phones/']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//*[@id="handsets"]/div[not(@class="alternate-list-item")]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', 'div/div/h3/strong/a/text()')
            if product.select('div/div/h3/strong/a/@href').extract():
                relative_urls = product.select('div/div/h3/strong/a/@href').extract()[0]
                url = urljoin_rfc('http://www.t-mobile.co.uk/',
                                  relative_urls, response.encoding)
            loader.add_value('url', url)
            loader.add_xpath('price', 'div/div/p/strong/text()')
            yield loader.load_item()
