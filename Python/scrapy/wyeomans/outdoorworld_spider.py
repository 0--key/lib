from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class OutdoorWorldSpider(BaseSpider):
    name = 'outdoorworld.co.uk'
    allowed_domains = ['outdoorworld.co.uk']
    start_urls = ['http://www.outdoorworld.co.uk/tents/tents-by-size?limit=all']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="category-products"]/ul/li')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('url', 'a/@href')
            loader.add_xpath('name', 'h2/a/@title')
            xpath = ('div[@class="price-box"]/'
                    'p[@class="special-price"]/span[@class="price"]/text()')
            if product.select(xpath):
                loader.add_xpath('price', xpath)
            else:
                xpath = ('div[@class="price-box"]/'
                        'p[@class="minimal-price"]/span[@class="price"]/text()')
                if product.select(xpath):
                    loader.add_xpath('price', xpath)
                else:
                    xpath = ('div[@class="price-box"]/'
                             'span[@class="regular-price"]/'
                             'span[@class="price"]/text()')
                    if product.select(xpath):
                        loader.add_xpath('price', xpath)
            yield loader.load_item()

        
