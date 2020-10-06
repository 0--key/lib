import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

class HadrianEquineSpider(BaseSpider):
    name = 'hadrianequine.co.uk'
    allowed_domains = ['www.hadrianequine.co.uk']
    start_urls = ('http://www.hadrianequine.co.uk/',)

    def __init__(self, *args, **kwargs):
        super(HadrianEquineSpider, self).__init__(*args, **kwargs)
        self.URLBASE = 'http://www.hadrianequine.co.uk'

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        
        # categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//div[@id="categorymenutop"]/ul/li/a/@href').extract()
        for url in category_urls:
            url = urljoin_rfc(self.URLBASE, url)
            yield Request(url)

        # subcategories and products
        for item in self.parse_product(response):
            yield item

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        # sub products
        hxs = HtmlXPathSelector(response)

        products = hxs.select('//div[@class="content-box"]/div[contains(@class,"item")]')
        for item in products:
            product = Product()
            price = item.select('.//div[@class="item-price"]').extract()
            url = item.select('.//div[@class="moreinfo"]/a/@href').extract()[0]
            url = urljoin_rfc(self.URLBASE, url)
            if not price:
                yield Request(url)
            else:
                loader = ProductLoader(item=product, response=response)
                try:
                    loader.add_value('url', url)
                    name = item.select('.//div[@class="item-name"]/a/text()').extract()[0]
                    loader.add_value('name', name)
                    loader.add_value('price', price)

                    loader.add_value('sku', '')

                    yield loader.load_item()
                except IndexError:
                    continue
  
