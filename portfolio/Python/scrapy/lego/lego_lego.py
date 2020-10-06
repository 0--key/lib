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

class LegoSpider(BaseSpider):
    name = 'lego-lego.com'
    allowed_domains = ['lego.com']

    def start_requests(self):
        with open(os.path.join(HERE, 'products.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                sku = row['sku']
                url = 'http://search2.lego.com/exec/?q=%s&lang=2057&cc=IT'
                yield Request(url % sku, meta={'sku': sku})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        product = hxs.select('//div[@class="single_product clearfix"]')
	cnt = 1
        if not product:
	    product = hxs.select('//div[@class="ThumbContainer1"]')
	    cnt = 2
	if not product:
	    return
	pr = None    
	if cnt>1:
	    for prd in product:
		loader = ProductLoader(item=Product(), selector=prd)
		url = prd.select('.//div[@class="ThumbImage"]//a/@href').extract()[0]
		if response.meta['sku'] in url:
		    loader.add_value('url', url)
		    loader.add_xpath('name', './/span[@class="underline"]/strong/text()')
		    nm = loader.get_output_value('name')
		    if not nm:
			loader.add_xpath('name', './/span[@class="underline"]/strong/i/text()')
        	    loader.add_value('sku', response.meta['sku'])
        	    loader.add_xpath('price', './/span[@class="Label1"]/text()')
		    pr = loader
		else:
		    continue
        else:
	    loader = ProductLoader(item=Product(), selector=product)
	    url = product.select('.//div[@class="product_image"]/a/@href').extract()[0]
	    if response.meta['sku'] in url:
		loader.add_value('url', url)
		loader.add_xpath('name', './/li[@class="product_title"]/text()')
        	loader.add_value('sku', response.meta['sku'])
        	price = product.select('.//div[@class="price"]/text()').extract()[1]
        	loader.add_value('price', price)
		pr = loader
	
	if pr:                                                                                                             
	    yield pr.load_item()    