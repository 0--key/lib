import re
import os
import json
import csv
import string
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader


from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))

class GadgetPandaSpider(BaseSpider):
    name = 'gadgetpanda.co.uk'
    allowed_domains = ['gadgetpanda.co.uk']
    start_urls = ['http://www.gadgetpanda.co.uk']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//*[@id="groupsel"]/option/@value').extract()
        for category in categories:
           url = 'http://www.gadgetpanda.co.uk/product.php?groupsel=%s' % category
           yield Request(url, callback=self.parse_category)

    def parse_category(self, response):
        hxs = HtmlXPathSelector(response)
        forms = hxs.select('//form')
        for form in forms:
            model = form.select('input/@value').extract()[0]
            name = form.select('div[@class="productDetails2"]/h3/text()').extract()[0]
            url = 'http://www.gadgetpanda.co.uk/product-details.php?model_id=%s&rdsizegrp=%s' 
            hd_ids = form.select('div[@class="productDetails2"]/div[@class="stripB"]/input/@value').extract()
            hd_desc = map(string.strip, form.select('div[@class="productDetails2"]/div[@class="stripB"]/text()').extract())
            if hd_desc:
                hd_desc = hd_desc[1:]
            hds = zip(hd_ids, hd_desc)
            if hds:
                for id, hd in hds:
                    yield Request(url % (model, id), callback=self.parse_product, 
                                  meta={'name':' '.join((name,hd))})
            else:
                yield Request(url % (model, ''), callback=self.parse_product, meta={'name':name})
  
    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        price = float(hxs.select('//*[@id="price"]/@value').extract()[0])
        values = map(float, hxs.select('//input[@type="radio" and @name!="radiofaulty"]/@value').extract())
        grade_values = dict(zip(['Grade A','Grade B','Grade C','Grade D'], values))
        ticks = hxs.select('//*[@id="qcontainer"]/div/input[@type="checkbox"]/@value').extract()
        total_ticks = sum(map(float, ticks))
        for grade, value in grade_values.iteritems():
            loader = ProductLoader(item=Product(), response=response)
            loader.add_value('name', ' '.join((response.meta['name'], grade)))
            loader.add_value('price', price-value-total_ticks)
            loader.add_value('url', response.url)
            yield loader.load_item()
        faulty = hxs.select('//input[@type="radio" and @name="radiofaulty"]/@value').extract()
        if faulty:
            loader = ProductLoader(item=Product(), response=response)
            loader.add_value('name', ' '.join((response.meta['name'], 'Grade E')))
            loader.add_value('price', faulty[0])
            loader.add_value('url', response.url)
            yield loader.load_item()
