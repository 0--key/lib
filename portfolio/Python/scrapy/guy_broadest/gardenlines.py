import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest
from product_spiders.items import ProductLoader, Product

class gardenlinesSpider(BaseSpider):

    name = "gardenlines.co.uk"
    allowed_domains = ["www.gardenlines.co.uk"]
    start_urls = ("http://www.gardenlines.co.uk/",)
    
    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        content = hxs.select("//div[@class='Menu']/ul/li")
        items = content.select(".//a/@href").extract()
                    
        for item in items:
            yield Request(urljoin_rfc(base_url,item), callback=self.parse_subcat)
            
    def parse_subcat(self,response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)
        content = hxs.select("//div[@class='Menu']/ul/li/ul[@class='SubMenu']/li")
        items = content.select(".//a/@href").extract()
                    
        for item in items:
            yield Request(urljoin_rfc(base_url,item), callback=self.parse_items)        
            
    def parse_items(self,response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)
        items = hxs.select("//div[@class='Content']/div/div/div/div/div[@class='MoreInfo']/@onclick").re(r'\'(.*)\'')
                    
        for item in items:
            yield Request(urljoin_rfc(base_url,item), callback=self.parse_item)        
                        
            
    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)

        name = hxs.select("//div[@class='Content']/div/h1/text()").re(r'([a-zA-Z0-9\-\_\.\(\)\&\#\%\@\!\*][a-zA-Z0-9\-\_\.\(\)\&\#\%\@\!\* ]+)')
        
        url = response.url
        price = hxs.select("//div[@class='Content']/div/div//h5/text()").re(r'\xa3([\.0-9,]*)')

        l = ProductLoader(item=Product(), response=response)
        l.add_value('name', name)        
        l.add_value('url', url)
        l.add_value('price', price)
        yield l.load_item()
