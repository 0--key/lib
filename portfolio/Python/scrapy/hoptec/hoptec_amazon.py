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

class AmazonfrSpider(BaseSpider):
 name = 'hoptec-amazon.fr'
 allowed_domains = ['amazon.fr']

 def start_requests(self):
  with open(os.path.join(HERE, 'products.csv')) as f:
   reader = csv.DictReader(f)
   for row in reader:
    sku = row['sku'].strip()
    url = 'http://www.amazon.fr/s/ref=nb_sb_noss_1?' + \
          'url=search-alias%%3Dwatches&field-keywords=%s&x=0&y=0'
    yield Request(url % sku, meta={'sku': sku})

 def parse(self, response):
  hxs = HtmlXPathSelector(response)
  products = hxs.select('//div[@id="atfResults"]//div[starts-with(@id, "result_0")]')
  pr = None
  if products:
   product = products[0]
   loader = ProductLoader(item=Product(), selector=product)
   loader.add_xpath('name', './/h3[@class="title"]/a/text()')
   product_name = loader.get_output_value('name').lower()
   loader.add_xpath('url', './/h3[@class="title"]/a/@href')
   price = product.select('.//div[@class="newPrice"]//span[@class="price"]/text()').extract()
   if not price:
    price = product.select('.//div[@class="usedNewPrice"]//span[@class="price"]/text()').extract()
   if price:
    loader.add_value('price', price[0].replace(',','.'))
   loader.add_value('sku', response.meta['sku'])
   pr = loader
   if pr and response.meta['sku'].lower() in product_name:
    yield pr.load_item()