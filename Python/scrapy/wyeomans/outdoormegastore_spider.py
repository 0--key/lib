from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class OutdoorMegastoreSpider(BaseSpider):
    name = 'outdoormegastore.co.uk'
    allowed_domains = ['outdoormegastore.co.uk']
    start_urls = ['http://www.outdoormegastore.co.uk/tents.html']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="category-products"]/ul/li')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('url', 'div/h2/a/@href')
            loader.add_xpath('name', 'div/h2/a/text()')
            price = ''.join(product.select('div/div[@class="price-box"]/'
                                           'p[@class="special-price"]/'
                                           'span[@class="price"]/text()').extract())
            if not price:
                price = ''.join(product.select('div/div[@class="price-box"]/'
                                               'span[@class="regular-price"]/'
                                               'span/text()').extract())
            loader.add_value('price', price)
            yield loader.load_item()
        next_page = hxs.select('//a[@class="next i-next"]/@href').extract()
        if next_page:
            url = next_page[-1].replace('ajax=1','')
            yield Request(url)
