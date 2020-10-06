import csv
import os
from scrapy import log
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.fuzzywuzzy import process
from product_spiders.fuzzywuzzy import fuzz

HERE = os.path.abspath(os.path.dirname(__file__))

class WharfAquaticsSpider(BaseSpider):
    name = 'wharfaquatics.co.uk'
    allowed_domains = ['wharfaquatics.co.uk']
    start_urls = ['http://www.wharfaquatics.co.uk/categories.asp']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//p[@class="catname"]/strong/a/@href').extract()
        for category in categories:
            url =  urljoin_rfc(get_base_url(response), category)
            yield Request(url, callback=self.parse_products, dont_filter=True)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//p[@class="catname"]/strong/a/@href').extract()
        if categories:
            yield Request(response.url, dont_filter=True)
        else:
            tr = ('<tr><td colspan="3" align="center" class="pagenums">'+
                 '<p class="pagenums">\r\n\t\t\t\t  '+
                 '<img src="images/clearpixel.gif" width="300" '+
                 'height="8" alt=""></p></td>\r\n\t\t\t  </tr>')
            tr_end = '<tr>' + hxs.select('//td[@class="prodseparator"]').\
                                  extract()[0].decode('utf') + '</tr>'
            html = hxs.extract().replace(tr,'<table class="item">').\
                       replace(tr_end,'</table><table class="item">')
            products_hxs = HtmlXPathSelector(text=html)
            products = products_hxs.select('//table[@class="item"]')
            for product in products:
                name = product.select('tr/td/strong/div[@class="prodname"]/a/text()').extract()
                if name:
                    name = name[0]
                    url = product.select('tr/td/strong/div[@class="prodname"]/a/@href').extract()
                    if url:
                        url = url[0]
                    price_options = product.select('tr/td/form/script').extract()
                    if price_options:
                        price_values = self._get_prices(price_options[0])
                        for price, desc in price_values:
                            loader = ProductLoader(item=Product(), selector=product)
                            loader.add_value('name', ' '.join((name,desc)))
                            loader.add_value('url', urljoin_rfc(get_base_url(response), url))
                            loader.add_value('price', price)
                            yield loader.load_item()
                    else:
                        price = product.select('tr/td/div[@class="prodprice"]/span/text()').extract()
                        if price:
                            price = price[0]
                        else:
                            price = 0.0
                        loader = ProductLoader(item=Product(), selector=product)   
                        loader.add_value('name', name)
                        loader.add_value('url', urljoin_rfc(get_base_url(response), url))
                        loader.add_value('price', price)
                        yield loader.load_item()
        next = hxs.select('//a[@class="ectlink" and @ rel="next"]/@href').extract()
        if next:
            url =  urljoin_rfc(get_base_url(response), next[0])
            yield Request(url, callback=self.parse_products)
         
    def _get_prices(self, script):
        prices = []
        for line in script.split('";')[:-1]:
            price, desc = line.split(';')
            prices.append((price.split('=')[-1], desc.split('="')[-1]))
        return prices
