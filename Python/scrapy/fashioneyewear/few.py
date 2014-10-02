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

class fewSpider(BaseSpider):

    name = "fashioneyewear.co.uk"
    allowed_domains = ["www.fashioneyewear.co.uk"]
    start_urls = ("http://www.fashioneyewear.co.uk/store/index.php/designer-frames-1.html",
                  "http://www.fashioneyewear.co.uk/designer-sunglasses.html",)
    
    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        content = hxs.select("//div[@class='brand_tile']")
        items = content.select(".//a/@href").extract()
                    
        for item in items:
            yield Request(urljoin_rfc(base_url,item), callback=self.parse_items)
             
            
    def parse_items(self,response):
        base_url = get_base_url(response)        
        hxs = HtmlXPathSelector(response)
        content = hxs.select("//div[@class='category-products']/ul/li/h2")
        items = content.select(".//a/@href").extract()
        for item in items:
            yield Request(item, callback=self.parse_item)
            
        items = hxs.select('//div[@class="pages"]/ol/li/a/@href').extract()
        for item in items:
            yield Request(urljoin_rfc(base_url,item), callback=self.parse_items_paged)     
            
        
        items = hxs.select('//div[@class="more_colours"]/a/@href').extract()
        for item in items:
            yield Request(item, callback=self.parse_item)                 

    def parse_items_paged(self,response):
        base_url = get_base_url(response)          
        hxs = HtmlXPathSelector(response)
        content = hxs.select("//div[@class='category-products']/ul/li/h2")
        items = content.select(".//a/@href").extract()
        for item in items:
            yield Request(item, callback=self.parse_item)

        items = hxs.select('//div[@class="pages"]/ol/li/a/@href').extract()
        for item in items:
            yield Request(urljoin_rfc(base_url,item), callback=self.parse_items_paged)       
            
        items = hxs.select('//div[@class="more_colours"]/a/@href').extract()
        for item in items:
            yield Request(item, callback=self.parse_item)
            
    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)   

        name = hxs.select("//div[@class='product-name']/h1/text()").extract()
        url = response.url
        price = "".join(hxs.select("//div[@class='product-shop hreview-aggregate']/div[@class='price-box']/span/span[@class='price']/text()").re(r'([0-9\,\. ]+)')).strip()
        #price = hxs.select("//div[@class='product-shop']/div[@class='price-box']/span/span[@class='price']/text()").re(r'\xa3([\.0-9]*)')
        if not price:
            price = "".join(hxs.select("//div[@class='product-shop hreview-aggregate']/div[@class='price-box']/p[@class='special-price']/span[@class='price']/text()").re(r'([0-9\,\. ]+)')).strip()
            #hxs.select("//div[@class='product-shop']/div[@class='price-box']/p[@class='special-price']/span[@class='price']/text()").re(r'\xa3([\.0-9]*)')

        l = ProductLoader(item=Product(), response=response)
        l.add_value('name', name)        
        l.add_value('url', url)
        l.add_value('price', price)
        yield l.load_item()
