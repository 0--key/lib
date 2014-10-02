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

class eyewearbrandsSpider(BaseSpider):

    name = "eyewearbrands.com"
    allowed_domains = ["www.eyewearbrands.com"]
    start_urls = ("http://www.eyewearbrands.com/designer%20glasses/gender/female/showall",
                  "http://www.eyewearbrands.com/designer%20glasses/gender/male/showall",
                  "http://www.eyewearbrands.com/prescription%20sunglasses/gender/female/showall",
                  "http://www.eyewearbrands.com/prescription%20sunglasses/gender/male/showall",)
    
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        content = hxs.select("//div[@class='cat_section2']/div[@class='cat_section_txt']")
        items = content.select(".//a/@href").extract()
                    
        for item in items:
            yield Request(item, callback=self.parse_item)
                        
            
    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)

        name = hxs.select("//div[@id='cprod_d']/span/h1/text()").extract()
        url = response.url
        price = hxs.select("//div[@id='cprod_price']/b/span[@class='cprod_saleprice']/text()").re(r'\xa3(.*)')
        if not price:
            price = hxs.select("//div[@id='cprod_price']/span[@class='cprod_price']/b/text()").re(r'\xa3(.*)')

        l = ProductLoader(item=Product(), response=response)
        l.add_value('name', name)        
        l.add_value('url', url)
        l.add_value('price', price)
        yield l.load_item()
