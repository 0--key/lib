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

       

class glasses123Spider(BaseSpider):

    name = "glasses123.co.uk"
    allowed_domains = ["www.glasses123.co.uk"]
    start_urls = ("http://www.glasses123.co.uk/store/categories.php?category=Brand-%252d-Carrera",
                  "http://www.glasses123.co.uk/store/categories.php?category=Brand-%252d-D%26G",
                  "http://www.glasses123.co.uk/store/categories.php?category=Brand-%252d-Dior",
                  "http://www.glasses123.co.uk/store/categories.php?category=Brand-%252d-DKNY",
                  "http://www.glasses123.co.uk/store/categories.php?category=Brand-%252d-Dolce-%26-Gabanna",
                  "http://www.glasses123.co.uk/store/categories.php?category=Brand-%252d-Emporio-Armani",
                  "http://www.glasses123.co.uk/store/categories.php?category=Brand-%252d-Gucci",
                  "http://www.glasses123.co.uk/store/categories.php?category=Brand-%252d-Hugo-Boss",
                  "http://www.glasses123.co.uk/store/categories.php?category=Brand-%252d-Oakley",
                  "http://www.glasses123.co.uk/store/categories.php?category=Brand-%252d-Polo",
                  "http://www.glasses123.co.uk/store/categories.php?category=Brand-%252d-Prada",
                  "http://www.glasses123.co.uk/store/categories.php?category=Brand-%252d-Ralph-Lauren",
                  "http://www.glasses123.co.uk/store/categories.php?category=Brand-%252d-Ray-Ban",
                  "http://www.glasses123.co.uk/store/categories.php?category=Category-%252d-Designer-Sunglasses",
                  )
    
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        content = hxs.select("//div[@class='SubCategoryListGrid']/ul/li")
        items = content.select(".//a/@href").extract()
                    
        for item in items:
            yield Request(item, callback=self.parse_catalog)
            
        content = hxs.select("//ul[@class='PagingList']/li")
        items = content.select(".//a/@href").extract()        
        for item in items:
            yield Request(item, callback=self.parse_items_paged)               
            
        content = hxs.select("//ul[@class='ProductList ']/li/div[@class='ProductImage']")
        items = content.select(".//a/@href").extract()
                    
        for item in items:
            yield Request(item, callback=self.parse_item)        
            
    def parse_catalog(self,response):
        hxs = HtmlXPathSelector(response)
        
        content = hxs.select("//ul[@class='PagingList']/li")
        items = content.select(".//a/@href").extract()        
        for item in items:
            yield Request(item, callback=self.parse_items_paged)               
            
        content = hxs.select("//ul[@class='ProductList ']/li/div[@class='ProductImage']")
        items = content.select(".//a/@href").extract()
                    
        for item in items:
            yield Request(item, callback=self.parse_item)             
        
    def parse_items_paged(self,response):
        hxs = HtmlXPathSelector(response)
        
        content = hxs.select("//ul[@class='ProductList ']/li/div[@class='ProductImage']")
        items = content.select(".//a/@href").extract()
                    
        for item in items:
            yield Request(item, callback=self.parse_item)          
        
        content = hxs.select("//ul[@class='PagingList']/li")
        items = content.select(".//a/@href").extract()
                    
        for item in items:
            yield Request(item, callback=self.parse_items_paged)     
        
                        
            
    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)

        name = hxs.select("//div[@class='BlockContent']/h2/text()").extract()
        url = response.url
        price = hxs.select("//em[@id='ProductPrice']/text()").re(r'\xa3(.*)')

        l = ProductLoader(item=Product(), response=response)

        l.add_value('name', name)        
        l.add_value('url', url)
        l.add_value('price', price)
        yield l.load_item()
