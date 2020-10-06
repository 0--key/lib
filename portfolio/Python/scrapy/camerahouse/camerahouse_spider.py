import csv
import os
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.fuzzywuzzy import process
from product_spiders.fuzzywuzzy import fuzz

HERE = os.path.abspath(os.path.dirname(__file__))

class CameraHouseSpider(BaseSpider):
    name = 'camerahouse.com.au'
    allowed_domains = ['camerahouse.com.au']
    start_urls = ['http://www.camerahouse.com.au/products.aspx']

    def __init__(self, *args, **kwargs):
        super(CameraHouseSpider, self).__init__(*args, **kwargs)
        csv_file = csv.reader(open(os.path.join(HERE, 'StockList.csv')))
        self.products = [(row[0],row[1]) for row in csv_file]


    def start_requests(self):
        for sku, name in self.products:
	    sku = sku.strip()
            name = name.strip()
            url = 'http://www.camerahouse.com.au/search-results.aspx?filter=&search='+sku
            yield Request(url, meta={'sku': sku, 'name': name})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="box_product"]')
        dict_products = {}
        #Obtains all the products of the first page of the search. 
        for product in products:
            name = product.select('a/h3/text()').extract()[0]
            url = url = urljoin_rfc(get_base_url(response), product.select('a/@href').extract()[0])
            price = product.select( 'div/div/div[@class="price"]/text()').extract()[0]
            dict_products[name] = [url, price]
        #Just loads one product using fuzzy matching.
        extracted = process.extractOne(response.meta['name'], dict_products.keys(), scorer=fuzz.token_set_ratio)    
        try:
            if extracted[1]>=92:
                loader = ProductLoader(item=Product(), response=response)
                loader.add_value('sku', response.meta['sku'])
                loader.add_value('name', extracted[0])
            
                loader.add_value('url', dict_products[extracted[0]][0])
                loader.add_value('price',dict_products[extracted[0]][1])
                yield loader.load_item()
        except TypeError: 
            return       


