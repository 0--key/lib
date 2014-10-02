import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest
from product_spiders.items import ProductLoader, Product

try:
    import json
except ImportError:
    import simplejson as json

class selectspecsSpider(BaseSpider):

    name = "selectspecs.com"
    allowed_domains = ["www.selectspecs.com"]
    urls = ("http://www.selectspecs.com/view/items/tab/3/cat/11/",
                  "http://www.selectspecs.com/view/items/tab/3/cat/10/",  
                  "http://www.selectspecs.com/Glasses/Prescription/BOSS-Hugo-Boss/d246/",
                  "http://www.selectspecs.com/Glasses/Prescription/Boss-Orange/d31396/",
                  "http://www.selectspecs.com/Glasses/Prescription/Bvlgari/d211/",
                  "http://www.selectspecs.com/Glasses/Prescription/Carrera/d35/",
                  "http://www.selectspecs.com/Glasses/Prescription/D-and-G/d83/",
                  "http://www.selectspecs.com/Glasses/Prescription/DKNY/d232/",
                  "http://www.selectspecs.com/Glasses/Prescription/Dolce-and-Gabbana/d109/",
                  "http://www.selectspecs.com/Glasses/Prescription/Emporio-Armani/d33/",
                  "http://www.selectspecs.com/Glasses/Prescription/Giorgio-Armani/d62/",
                  "http://www.selectspecs.com/Glasses/Prescription/Gucci/d60/",
                  "http://www.selectspecs.com/Glasses/Prescription/HUGO-Hugo-Boss/d390/",
                  "http://www.selectspecs.com/Glasses/Prescription/JIMMY-CHOO/d395/",
                  "http://www.selectspecs.com/Glasses/Prescription/Marc-by-Marc-Jacobs/d389/",
                  "http://www.selectspecs.com/Glasses/Prescription/Marc-Jacobs/d387/",
                  "http://www.selectspecs.com/Glasses/Prescription/Mont-Blanc/d285/",
                  "http://www.selectspecs.com/Glasses/Prescription/Oakley/d391/",
                  "http://www.selectspecs.com/Glasses/Prescription/Oakley-Ladies/d399/",
                  "http://www.selectspecs.com/Glasses/Prescription/Persol/d208/",
                  "http://www.selectspecs.com/Glasses/Prescription/Ralph-Lauren/d233/",
                  "http://www.selectspecs.com/Glasses/Prescription/Prada/d111/",
                  "http://www.selectspecs.com/Glasses/Prescription/Prada-Red-Sport-Linea-Rossa/d338/",
                  "http://www.selectspecs.com/Glasses/Prescription/Ralph-Lauren/d233/",
                  "http://www.selectspecs.com/Glasses/Prescription/Ray-Ban/d43/",
                  "http://www.selectspecs.com/Glasses/Prescription/Tom-Ford/d284/",
                  )
    
    def start_requests(self): 
        return [FormRequest(
            url='http://www.selectspecs.com/auth/changeCurrency', 
            formdata={'curr':'gbp'},
            callback=self.parse)]          
    
    def parse(self, response):
        for url in self.urls:
            yield Request(url, callback=self.parce_catalog)        
            

    def parce_catalog(self,response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)                   
        content = hxs.select("//div[@class='itemImage']")
        items = content.select(".//a/@href").extract()
                    
        for item in items:
            yield Request(urljoin_rfc(base_url,item),cookies={'currency': '1','language':'1'}, callback=self.parse_item)
        
        items = hxs.select('//div[@class="pagination"]/a[@class="number"]/@href').extract()
        for item in items:
            yield Request(urljoin_rfc(base_url,item),cookies={'currency': '1','language':'1'}, callback=self.parse_items_paged)                       
        
        

    def parse_items_paged(self,response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)                   
        content = hxs.select("//div[@class='itemImage']")
        items = content.select(".//a/@href").extract()
                    
        for item in items:
            yield Request(urljoin_rfc(base_url,item),cookies={'currency': '1','language':'1'}, callback=self.parse_item)

        items = hxs.select('//div[@class="pagination"]/a[@class="number"]/@href').extract()
        for item in items:
            yield Request(urljoin_rfc(base_url,item),cookies={'currency': '1','language':'1'}, callback=self.parse_items_paged)          
            
    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)

        name1 = hxs.select("//div[@class='rightCol']/h1/text()").re(r'^(.*)Prescription Glasses.*')
        if not name1:
            name1 = hxs.select("//div[@class='rightCol']/h1/text()").re(r'^(.*)Designer Sunglasses.*');
        name2 = hxs.select("//div[@class='rightCol']/h1/text()").re(r', (.*)\.')
        name = name1[0] + name2[0];
        url = response.url
        price = hxs.select("//div[@class='rightCol']/span[@class='newprice']/text()").re(r'\xa3(.*)')
        #price = round((float(price[0])*0.20),2) + float(price[0]); # ADD VAT
        #price = str(price)
        price = price[0]
        

        l = ProductLoader(item=Product(), response=response)
        l.add_value('name', name)        
        l.add_value('url', url)
        l.add_value('price', price)
        yield l.load_item()
