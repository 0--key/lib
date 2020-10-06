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

class ElbashopSpider(BaseSpider):
 name = 'lego-elbashop.it'
 allowed_domains = ['elbashop.it']
 skus = []

 def start_requests(self):
  with open(os.path.join(HERE, 'products.csv')) as f:
   reader = csv.DictReader(f)
   for row in reader:
    self.skus.append(row['sku'])
   search_url = 'http://www.elbashop.it/modules/blocks/search/action_search.php'
   yield FormRequest(url=search_url,formdata={'fld_key': 'Lego', 'ckTipo': 'and', 'btn_0_ok': ''})

 def parse(self, response):
  hxs = HtmlXPathSelector(response)
  pgmax = 0
  pagination = hxs.select('//div[@class="label"]/text()').extract()
  if pagination:
   pgmax = int(pagination[0].split(' ')[-1])+1
  for pg in range(1,pgmax):
   yield Request('http://www.elbashop.it/catalog/pg/' + str(pg),callback=self.parse_page)

 def parse_page(self, response):
  hxs = HtmlXPathSelector(response)
  products = hxs.select('//div[@class="productIconsContainer"]')
  for product in products:
   product_name = product.select('.//div[@class="productIconsTitle"]/text()').extract()[0]
   sku_name = product_name.split(' ')
   if sku_name:
    sku = sku_name[0]
    if sku in self.skus:
     l = ProductLoader(item=Product(), selector=product)
     l.add_value('name', product_name)
     l.add_value('url', 'http://www.elbashop.it' + product.select('.//a/@href').extract()[0])
     l.add_value('sku', sku)
     l.add_value('price', product.select('.//td[@class="productIconsPrice"]//text()').extract()[0].replace(',','.'))
     yield l.load_item()
