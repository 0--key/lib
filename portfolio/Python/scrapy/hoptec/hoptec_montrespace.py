import csv
import os
import copy

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.http.cookies import CookieJar

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class MontrespaceSpider(BaseSpider):
 name = 'hoptec-montrespace.com'
 allowed_domains = ['montrespace.com']

 def start_requests(self):
  with open(os.path.join(HERE, 'products.csv')) as f:
   reader = csv.DictReader(f)
   for row in reader:
    sku = row['sku']
    url = 'http://www.montrespace.com/catalogsearch/result/?q=%s'
    yield Request(url % sku.strip(), meta={'sku': sku})

 def parse(self, response):
  hxs = HtmlXPathSelector(response)
  products = hxs.select('.//table[@id="product-list-table"]/tr/td')
  if products:
   pr = None
   product = products[0]
   loader = ProductLoader(item=Product(), selector=product)
   loader.add_xpath('name', './/h5/a/text()')
   url = product.select(u'.//h5/a/@href').extract()[0]
   loader.add_value('url', urljoin_rfc(get_base_url(response), url))
   loader.add_value('sku', response.meta['sku'])
   loader.add_value('price', 0)
   price = product.select('.//p[@class="special-price"]//span[@class="price"]/text()').extract()
   if not price:
    price = product.select('.//span[@class="regular-price"]//span[@class="price"]/text()').extract()
   if price:
    loader.add_value('price', price[0].replace(',','.'))
   pr = loader
   if pr:
    yield pr.load_item()