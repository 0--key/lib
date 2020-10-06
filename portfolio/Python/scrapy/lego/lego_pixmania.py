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

class PixmaniaSpider(BaseSpider):
    name = 'lego-pixmania.com'
    allowed_domains = ['pixmania.com']

    def start_requests(self):
        with open(os.path.join(HERE, 'products.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                sku = row['sku']
                url = 'http://www.pixmania.com/it/it/search/lego-%s'
                yield Request(url % sku, meta={'sku': sku})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//tr[@class="prd first"]')
        if products:
	    pr = None
	    product = products[0]
	    loader = ProductLoader(item=Product(), selector=product)
	    loader.add_xpath('name', './/h3/a/text()')
            loader.add_xpath('url', './/h3/a/@href')
	    loader.add_value('sku', response.meta['sku'])
	    loader.add_value('price', 0)
	    price = product.select('.//p[@class="prd-amount"]/strong/text()').extract()
	    if price:
		loader.add_value('price', price[0].replace(',','.'))
	    pr = loader
	    if pr:
		if price:
		    yield pr.load_item()
		else:
		    yield Request(pr.get_output_value('url'), callback=self.parse_product,meta={'cur_prod': pr}, dont_filter=True)

    def parse_product(self, response):
	hxs = HtmlXPathSelector(response)
	cur_prod = response.meta['cur_prod']
	if not cur_prod.get_output_value('price'):
	    price = hxs.select('.//span[@itemprop="price"]/text()').extract()
	    if price:
		cur_prod.add_value('price', price[0].replace(',','.'))
	yield cur_prod.load_item()