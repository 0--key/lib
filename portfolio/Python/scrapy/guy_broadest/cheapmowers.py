import re
import types
import os
import csv

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest
from product_spiders.items import ProductLoader, Product

HERE = os.path.abspath(os.path.dirname(__file__))
CSV_FILENAME = os.path.join(os.path.dirname(__file__), 'cheapmowers.csv')

class cheapmowersSpider(BaseSpider):

    name = "cheapmowers.com"
    allowed_domains = ["www.cheapmowers.com"]
    start_urls = ("http://www.cheapmowers.com/acatalog/Products_By_Brand.html",)

    def __init__(self, *args, **kwargs):
        super(cheapmowersSpider, self).__init__(*args, **kwargs)
        self.names = {}
        with open(CSV_FILENAME) as f:
           reader = csv.DictReader(f)
           for row in reader:
               self.names[row['url']] = row['name'].decode('utf-8', 'ignore')

    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        content = hxs.select("//table/tr/td[@height='77']")
        items = content.select(".//a/@href").extract()
                    
        for item in items:
            yield Request(urljoin_rfc(base_url,item), callback=self.parse_subcat)
        
        yield Request(urljoin_rfc(base_url,item), callback=self.parse_item)
            
    def parse_subcat(self,response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        content = hxs.select("//table/tr/td[@height='77']")
        items = content.select(".//a/@href").extract()
                    
        for item in items:
            yield Request(urljoin_rfc(base_url,item), callback=self.parse_subcat)
            
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        content = hxs.select("//table/tr/td/div[@align='left']")
        items = content.select(".//a/@href").extract()
                    
        for item in items:
            yield Request(urljoin_rfc(base_url,item), callback=self.parse_item)                      
                        
            
    def parse_item(self, response):
        if not re.search('index.html', str(response.url)):

            hxs = HtmlXPathSelector(response)
    
            name = hxs.select("//h1[@class='product']/strong/text()").extract()[0].strip()
            name = name.replace(u'\u00ae', u'')
            
            url = response.url
            price = hxs.select("//h2/span/strong/text()").re(r'\xa3([\.0-9,]*)')
            
            if name:
                l = ProductLoader(item=Product(), response=response)
                l.add_value('name', self.names.get(url, name))
                l.add_value('url', url)
                l.add_value('price', price)
                yield l.load_item()
