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

class EbayfrSpider(BaseSpider):
 name = 'hoptec-ebay.fr'
 allowed_domains = ['ebay.fr']

 def start_requests(self):
  with open(os.path.join(HERE, 'products.csv')) as f:
   reader = csv.DictReader(f)
   for row in reader:
    sku = row['sku'].strip()
    url = 'http://shop.ebay.fr/i.html?_sacat=281&_nkw=%s'
    yield Request(url % sku, meta={'sku': sku})

 def parse(self, response):
  hxs = HtmlXPathSelector(response)
  products = hxs.select('//table[@class="lvt"]')
  pr = None
  if products:
   product = products[0]
   loader = ProductLoader(item=Product(), selector=product)
   loader.add_xpath('name', './/div[@class="lv-pb5 lv-title-box"]/a/text()')
   loader.add_xpath('url', '//div[@class="lv-pb5 lv-title-box"]/a/@href')
   price = product.select('.//div[@class="lv-dvpr"]/div[@class="lv-pb5"]/b/text()').extract()
   if price:
    loader.add_value('price', price[0].replace(',','.'))
   loader.add_value('sku', response.meta['sku'])
   pr = loader
   if pr:
    yield pr.load_item()