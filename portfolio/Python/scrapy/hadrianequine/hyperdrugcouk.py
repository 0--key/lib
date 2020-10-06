import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

class HyperDrugSpider(BaseSpider):
    name = 'hyperdrug.co.uk'
    allowed_domains = ['www.hyperdrug.co.uk']
    start_urls = ('http://www.hyperdrug.co.uk/AllProducts.asp',)

    def __init__(self, *args, **kwargs):
        super(HyperDrugSpider, self).__init__(*args, **kwargs)
        self.URLBASE = 'http://www.hyperdrug.co.uk/'

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # brands
        brand_urls = hxs.select('//span//a[@class="allpage"]/@href').extract()
        for url in brand_urls:
            url = urljoin_rfc(self.URLBASE, url)
            yield Request(url)

        # products
        products_urls = hxs.select('//td[@class="pagenavbg"]//a[@class="allpage" and not(ancestor::span)]/@href').extract()
        for url in products_urls:
            url = urljoin_rfc(self.URLBASE, url)
            yield Request(url, priority=1, callback=self.parse_product)
        

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        name = hxs.select('//h1/text()').extract()[0]
        
        multiple_prices = hxs.select('//select[@class="smalltextblk"]/option/text()').extract()
        single_special_price = hxs.select('//span/text()').re('\xa3(.*[0-9]+)')
        single_price = hxs.select('//td[@class="ProductPrice"]/text()').re('\xa3(.*[0-9])')
        
        products_data = []

        if single_price and not multiple_prices:
            price = single_price[0] if not single_special_price else single_special_price[0]
            products_data.append((name, price))
        else:
            multiple_prices = multiple_prices[1:]
            for name_and_price in multiple_prices:
                name_and_price = re.match('(.*)\xa3(.*\.[0-9]+)', name_and_price).groups()
                products_data.append((name + ' ' + name_and_price[0], name_and_price[1]))

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
  
