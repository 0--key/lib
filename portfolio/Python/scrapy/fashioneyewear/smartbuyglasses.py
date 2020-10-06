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

       

class smartbuyglassesSpider(BaseSpider):

    name = "smartbuyglasses.co.uk"
    allowed_domains = ["www.smartbuyglasses.co.uk"]
    start_urls = ("http://www.smartbuyglasses.co.uk/designer-sunglasses/general/--------------",
                  "http://www.smartbuyglasses.co.uk/designer-eyeglasses/general/--------------",
                  "http://www.smartbuyglasses.co.uk/sports-sunglasses/Baseball/----------",
                  "http://www.smartbuyglasses.co.uk/sports-sunglasses/Lifestyle/----------",
                  "http://www.smartbuyglasses.co.uk/sports-sunglasses/Beach%20Volleyball/----------",
                  "http://www.smartbuyglasses.co.uk/sports-sunglasses/Climbing/----------",
                  "http://www.smartbuyglasses.co.uk/sports-sunglasses/Cricket/----------",
                  "http://www.smartbuyglasses.co.uk/sports-sunglasses/Cycling/----------",
                  "http://www.smartbuyglasses.co.uk/sports-sunglasses/Driving/----------",
                  "http://www.smartbuyglasses.co.uk/sports-sunglasses/Fishing/----------",
                  "http://www.smartbuyglasses.co.uk/sports-sunglasses/Golf/----------",
                  "http://www.smartbuyglasses.co.uk/sports-sunglasses/Surfing/----------",
                  "http://www.smartbuyglasses.co.uk/sports-sunglasses/Motorcycle/----------",
                  "http://www.smartbuyglasses.co.uk/sports-sunglasses/Outdoor/----------",
                  "http://www.smartbuyglasses.co.uk/sports-sunglasses/Running/----------",
                  "http://www.smartbuyglasses.co.uk/sports-sunglasses/Sailing/----------",
                  "http://www.smartbuyglasses.co.uk/sports-sunglasses/Tactical/----------",
                  "http://www.smartbuyglasses.co.uk/sports-sunglasses/Tennis/----------",
                  "http://www.smartbuyglasses.co.uk/sports-sunglasses/Ski%20Goggles/----------",
                  "http://www.smartbuyglasses.co.uk/sports-sunglasses/MX%20Goggle/----------",
                  "http://www.smartbuyglasses.co.uk/sports-sunglasses/Women/----------",
                  "http://www.smartbuyglasses.co.uk/sports-sunglasses/Junior%20Kids/----------",
                  )
    
    def parse(self, response):
        base_url = get_base_url(response)              
        hxs = HtmlXPathSelector(response)
        items = hxs.select("//div[@class='navArea']/div[@class='navAreaPagging fr']/span[@class='paggingBtnNext']/a/@href").extract()
                    
        for item in items:
            yield Request(urljoin_rfc(base_url,item), callback=self.parse)
            
        content = hxs.select("//div[@class='mainProducts']")
        products = content.select(".//a")
                    
        for product_ in products:
    
            name =  product_.select(".//ul/li/span[@class='productName']/text()").extract()
            url = product_.select(".//@href").extract()
            price =  product_.select(".//ul//li/ul/li[1]/span[@class='orange']/text()").re(r'\xa3(.*)')
            if not price:
                price =  product_.select(".//ul/li/ul/li[1]/span[@class='gray']/text()").re(r'\xa3(.*)')
            if name:
                l = ProductLoader(item=Product(), response=response)
                l.add_value('name', name)        
                l.add_value('url', url)
                l.add_value('price', price)
                l.load_item()
                yield l.load_item()            

            
            
        """content = hxs.select("//div[@class='mainProducts']")
        items = content.select(".//ul/li[@class='proIcon']/a/@href").extract()
                    
        for item in items:
            yield Request(item, callback=self.parse_item)"""
                                       
                           
                       
            
    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)

        name =  hxs.select("//tr[@class='model']/td[1]/h4[@class='seo']/text()").extract()
        if not name:
            name = hxs.select("//tr[@class='model']/td[1]/text()").extract()
        url = response.url
        price =  hxs.select("//tr[@class='price']/td/span/text()").re(r'\xa3(.*)')
        if not price:
            price =  hxs.select("//tr[@class='price']/td/text()").re(r'\xa3(.*)')

        l = ProductLoader(item=Product(), response=response)
        l.add_value('name', name[0])        
        l.add_value('url', url)
        l.add_value('price', price)
        yield l.load_item()