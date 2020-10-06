import re
import os
import json
import csv
from scrapy import log
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))

class CashMyIpodSpider(BaseSpider):
    name = 'cashmyipod.co.uk'
    allowed_domains = ['cashmyipod.co.uk']

    def __init__(self, *args, **kwargs):
        super(CashMyIpodSpider, self).__init__(*args, **kwargs)
        csv_file = csv.reader(open(os.path.join(HERE, 'cashmyipod_ids.csv')))
        self.products = {row[2]:row[1] for row in csv_file}
        csv_file = csv.reader(open(os.path.join(HERE, 'cashmyipod_last_names.csv')))
        self.last_names = {' '.join(row[0].lower().split()):row[0] for row in csv_file}

    def start_requests(self):
        for url, name in self.products.iteritems():
            yield Request(url, meta = {'name': name})

    def parse(self, response):
        URL = 'http://cashmygadget.co.uk/calculate_price.php'
        hxs = HtmlXPathSelector(response)
        id =  hxs.select('//*[@id="product_id"]/@value').extract()[0]
        form_static = {'product': id, 'action':'calculate'}
        attribute_10 = hxs.select('//*[@id="attribute_id_10"]/option[text()="0" or text()="None"]/@value').extract()
        if attribute_10:
            form_static['attribute_id_10'] = attribute_10[0]
        if hxs.select('//*[@id="attribute_id_11"]').extract():
            form_static['attribute_id_11'] = '99'
        if hxs.select('//*[@id="attribute_id_20"]').extract():
            form_static['attribute_id_20'] = '206'
        if hxs.select('//*[@id="attribute_id_14"]').extract():
            form_static['attribute_id_14'] = '135'
        if hxs.select('//*[@id="attribute_id_8"]').extract():
            form_static['attribute_id_8'] = '84'
        value_grades = hxs.select('//*[@id="product_grade"]/option[@value!=""]')
        value_grades = [ (h.select('@value').extract()[0], h.select('text()').extract()[0]) for h in value_grades]
        value_hdds = hxs.select('//*[@id="attribute_id_2"]/option[@value!=""]')
        value_hdds = [ (h.select('@value').extract()[0], h.select('text()').extract()[0]) for h in value_hdds]
        value_colors = hxs.select('//*[@id="attribute_id_13"]/option[@value!=""]')
        value_colors = [ (h.select('@value').extract()[0], h.select('text()').extract()[0]) for h in value_colors] 
        value_mems = hxs.select('//*[@id="attribute_id_12"]/option[@value!=""]')
        value_mems = [ (h.select('@value').extract()[0], h.select('text()').extract()[0]) for h in value_mems]
         
        for value_grade in value_grades:
            if value_colors:
                for value_color in value_colors:
                    if value_hdds:
                        for value_hdd in value_hdds:
                            form_data = form_static
                            form_data['product_grade'] = value_grade[0]
                            form_data['attribute_id_2'] = value_hdd[0]
                            form_data['attribute_id_13'] = value_color[0]
                            product = [response.meta['name']]
                            product.append(value_hdd[1])
                            product.append(value_color[1])
                            product.append(value_grade[1])
                            name = ' '.join(product)
                            if ' '.join(name.lower().split()) in self.last_names:
                                name = self.last_names[' '.join(name.lower().split())]
                            yield FormRequest(URL, method='POST',
                                             formdata=form_data, 
                                             dont_filter=True, 
                                             callback=self.parse_price,
                                             meta={'name':name, 'url':response.url})
                    else:
                        for value_mem in value_mems:
                            form_data = form_static
                            form_data['product_grade'] = value_grade[0]
                            form_data['attribute_id_12'] = value_mem[0]
                            form_data['attribute_id_13'] = value_color[0]
                            product = [response.meta['name']]
                            product.append(value_mem[1])
                            product.append(value_color[1])
                            product.append(value_grade[1])
                            name = ' '.join(product)
                            if ' '.join(name.lower().split()) in self.last_names:
                                name = self.last_names[' '.join(name.lower().split())]
                            yield FormRequest(URL, method='POST',
                                              formdata=form_data, 
                                              dont_filter=True, 
                                              callback=self.parse_price,
                                              meta={'name':name, 'url':response.url})
            else:
                 if value_hdds:
                        for value_hdd in value_hdds:
                            form_data = form_static
                            form_data['product_grade'] = value_grade[0]
                            form_data['attribute_id_2'] = value_hdd[0]
                            product = [response.meta['name']]
                            product.append(value_hdd[1])
                            product.append(value_grade[1])
                            name = ' '.join(product)
                            if ' '.join(name.lower().split()) in self.last_names:
                                name = self.last_names[' '.join(name.lower().split())]
                            yield FormRequest(URL, method='POST',
                                             formdata=form_data, 
                                             dont_filter=True, 
                                             callback=self.parse_price,
                                             meta={'name':name, 'url':response.url})
                 else:
                     if value_mems:
                         for value_mem in value_mems:
                             form_data = form_static
                             form_data['product_grade'] = value_grade[0]
                             form_data['attribute_id_12'] = value_mem[0]
                             product = [response.meta['name']]
                             product.append(value_mem[1])
                             product.append(value_grade[1])
                             name = ' '.join(product)
                             if ' '.join(name.lower().split()) in self.last_names:
                                 name = self.last_names[' '.join(name.lower().split())]
                             yield FormRequest(URL, method='POST',
                                               formdata=form_data, 
                                               dont_filter=True, 
                                               callback=self.parse_price,
                                               meta={'name':name, 'url':response.url})
                     else:
                         form_data = form_static
                         form_data['product_grade'] = value_grade[0]
                         product = [response.meta['name']]
                         product.append(value_grade[1])
                         name = ' '.join(product)
                         if ' '.join(name.lower().split()) in self.last_names:
                             name = self.last_names[' '.join(name.lower().split())]
                         yield FormRequest(URL, method='POST',
                                           formdata=form_data, 
                                           dont_filter=True, 
                                           callback=self.parse_price,
                                           meta={'name':name, 'url':response.url})

    def parse_price(self, response):
        hxs = HtmlXPathSelector(response)
        price = hxs.select('//p/span/text()').extract()[0]
        loader = ProductLoader(item=Product(), response=response)
        loader.add_value('name', response.meta['name'])
        loader.add_value('url', response.meta['url'])
        loader.add_value('price', price)
        yield loader.load_item()
        
