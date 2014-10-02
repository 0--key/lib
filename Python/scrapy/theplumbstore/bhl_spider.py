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

class ThePlumbStoreSpider(BaseSpider):
    name = 'bhl.co.uk'
    allowed_domains = ['bhl.co.uk']
    start_urls = ['http://www.bhl.co.uk']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//div[@class="subnav"]/dl/dt/a/@href').extract()
        for category in categories:
            url =  urljoin_rfc(get_base_url(response), category)
            yield Request(url, callback=self.parse_products, meta={'do_pagination':True})

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="prod"]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)   
            #loader.add_xpath('name', 'div/form/fieldset/div/h5/a/span/text()')
            name = product.select('div/form/fieldset/div/h5/a/span/text()').extract()[0].strip()
            url = product.select('div/form/fieldset/div/h5/a/@href').extract()
            if url:
                url =  urljoin_rfc(get_base_url(response), url[0])
            #loader.add_value('url', url)
            #loader.add_xpath('price', 'div/form/fieldset/div/span[@class="productPrice priceExVAT"]/text()')
            #yield loader.load_item()
            price = product.select('div/form/fieldset/div/span[@class="productPrice priceExVAT"]/text()').extract()[0].strip()
            yield Request(url, callback=self.parse_product, meta={'name':name, 'price':price})
        pages = hxs.select('//span[@class="pagingButton"]/a/@href').extract()
        if pages:
            if response.meta['do_pagination']:
                for page in pages:
                    url =  urljoin_rfc(get_base_url(response), page)
                    yield Request(url, callback=self.parse_products, meta={'do_pagination':False})
        else:
            sub_categories = hxs.select('//div[@class="subcat"]/div/a/@href').extract()
            for sub_category in sub_categories:
                url =  urljoin_rfc(get_base_url(response), sub_category)
                yield Request(url, callback=self.parse_products, meta={'do_pagination':True}) 

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        loader = ProductLoader(item=Product(), response=response) 
        mpn = ''.join(hxs.select('//div[@class="span-4 productcolumn productleftcol"]/h4[text()="Manufacturers Part No:"]/span/text()').extract())
        loader.add_value('identifier', mpn)
        loader.add_value('url', response.url)
        loader.add_value('name', ' '.join((response.meta['name'], mpn)))
        loader.add_value('price', response.meta['price'])
        yield loader.load_item()
