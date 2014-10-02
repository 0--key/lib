import csv
import os
import copy
import shutil

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.http.cookies import CookieJar
from scrapy import log

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class PickyourshoesSpider(BaseSpider):
    name = 'pickyourshoes.com'
    allowed_domains = ['pickyourshoes.com','www.pickyourshoes.com']

    def start_requests(self):
        shutil.copy(os.path.join(HERE, 'shoemetroall.csv'),os.path.join(HERE, 'shoemetroall.csv.' + self.name + '.cur'))
        with open(os.path.join(HERE, 'shoemetroall.csv.' + self.name + '.cur')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                sku = row['sku']
                """
                brand = row['brand']
                style = row['style']
                query = (brand + ' ' + style).replace(' ', '+')
                """
                query = row['name'].replace(' ', '+')
                url = 'http://www.pickyourshoes.com/search.asp?itemname=%s'
                yield Request(url % query, meta={'sku': sku, 'name': query})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        products = hxs.select('//td[@style="padding:15px 0 10px 5px;"]')

        if not products:
            return
        product = products[0]

        url = product.select('./a/@href').extract()
        if url:
            yield Request(url[0], callback=self.parse_product, meta={'sku': response.meta['sku']})
        


    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        name = hxs.select('//td[@style="padding-left:10px;"]/h1/text()').extract()
        
        loader = ProductLoader(item=Product(), response=response)
        
        if name:
            price = "".join(hxs.select('.//p[@class="productDesc"]/span[@class="price"]/text()').re(r'([0-9\,\. ]+)')).strip()
            loader.add_value('name', name[0].strip() )
            loader.add_value('url', response.url)
            loader.add_value('price', price)
            loader.add_value('sku', response.meta['sku'])

            if not 'apparelsave' in loader.get_output_value('name').lower():
                yield loader.load_item()
      
      
      
      