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

class MontingSpider(BaseSpider):
 name = 'hoptec-monting.fr'
 allowed_domains = ['monting.fr']

 def start_requests(self):
  with open(os.path.join(HERE, 'products.csv')) as f:
   reader = csv.DictReader(f)
   for row in reader:
    sku = row['sku'].strip()
    url = 'http://www.monting.fr/recherche.php?q=%s'
    yield Request(url % sku, meta={'sku': sku})

 def parse(self, response):
  hxs = HtmlXPathSelector(response)
  products = hxs.select('//div[@class="mini noheader"]')
  pr = None
  if products:
   product = products[0]
   loader = ProductLoader(item=Product(), selector=product)
   loader.add_xpath('name', './/p/a/text()')
   url = product.select(u'.//p/a/@href').extract()[0]
   loader.add_value('url', urljoin_rfc(get_base_url(response), url))
   loader.add_xpath('price', './/span[@class="prix"]/text()')
   loader.add_value('sku', response.meta['sku'])
   pr = loader
   if pr:
    yield pr.load_item()