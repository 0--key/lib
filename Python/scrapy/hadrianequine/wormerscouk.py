import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

class WormersSpider(BaseSpider):
    name = 'wormers.co.uk'
    allowed_domains = ['www.wormers.co.uk']
    start_urls = ('http://www.wormers.co.uk/',)

    def __init__(self, *args, **kwargs):
        super(WormersSpider, self).__init__(*args, **kwargs)
        self.URLBASE = 'http://www.wormers.co.uk/'

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        
        # categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//a[@class="product_section"]/@href').extract()
        for url in category_urls:
            url = urljoin_rfc(self.URLBASE, url)
            yield Request(url)

        # subcategories
        subcategory_urls = hxs.select('//tr/td/a[contains(@href,"SECTIONID")]/img/../@href').extract()
        for url in subcategory_urls:
            yield Request(url)

        # products
        products_urls = hxs.select('//h1/a/@href').extract()
        for url in products_urls:
            url = urljoin_rfc(self.URLBASE + 'acatalog/', url)
            yield Request(url, callback=self.parse_product)
        

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        # sub products
        hxs = HtmlXPathSelector(response)

        # multiple prices
        name = hxs.select('//h1/text()').extract()[0]
        multiple_prices = hxs.select('//option/text()').extract()
        single_price = hxs.select('//span/b/text()').re('\xa3(.*)')
        products_data = []
        if not single_price:
            for name_and_price in multiple_prices:
              #  try:
                name_and_price = re.sub('[\t\r\n]', '', name_and_price).strip()
                products_data.append(re.match('(.*[0-9,a-z,A-Z\)]).*\xa3(.*[0-9])', name_and_price).groups())
              #  except AttributeError:
              #      continue
        else:
            price = single_price[0]
            products_data.append((name, price), )

        for item in products_data:
            product = Product()
            loader = ProductLoader(item=product, response=response)
            # try:
            loader.add_value('url', response.url)
            loader.add_value('name', item[0])
            loader.add_value('price', item[1])

            loader.add_value('sku', '')

            yield loader.load_item()
            # except IndexError:
                # return
  
