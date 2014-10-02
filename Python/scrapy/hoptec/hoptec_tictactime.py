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

class TictacSpider(BaseSpider):
 name = 'hoptec-tictactime.com'
 allowed_domains = ['tictactime.com']
 skus = []
 skusl = []

 def start_requests(self):
  with open(os.path.join(HERE, 'products.csv')) as f:
   reader = csv.DictReader(f)
   for row in reader:
    self.skus.append(row['sku'])
    self.skusl.append(row['sku'].lower())
   for pg in range(1,10):
    url = 'http://www.tictactime.com/accessoires-de-mode-montres-cadeau-montres-casio-_______1____111_' + str(pg) + '___________________________.html'
    yield Request(url)

 def parse(self, response):
  hxs = HtmlXPathSelector(response)
  products = hxs.select('//div[@class="vign_standard"]')
  for product in products:
   product_name = product.select('.//div[@class="vign_element1"]/a/text()').extract()[0]
   sku_name = product.select('.//div[@class="vign_element2"]/a/text()').extract()
   if sku_name:
    sku = sku_name[0]
    if sku.lower() in self.skusl:
     l = ProductLoader(item=Product(), selector=product)
     l.add_value('name', product_name + ' - ' + sku)
     url = product.select(u'.//div[@class="vign_element2"]/a/@href').extract()[0]
     l.add_value('url', urljoin_rfc(get_base_url(response), url))
     l.add_value('sku', sku)
     price = product.select('.//div[@class="vign_groupe_prix"]//span[@class="vign_prix_rouge"]/text()').extract()
     if not price:
      price = product.select('.//div[@class="vign_groupe_prix"]//span[@class="vign_prix"]/text()').extract()
     if price:
      l.add_value('price', price[0])
     yield l.load_item()
