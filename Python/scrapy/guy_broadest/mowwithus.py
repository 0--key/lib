import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.conf import settings

#settings.overrides['DOWNLOAD_DELAY'] = 6

from productloader import load_product
from scrapy.http import FormRequest
from product_spiders.items import ProductLoader, Product

class nowwithusSpider(BaseSpider):    
    download_delay = 6
    name = "mowwithus.com"
    allowed_domains = ["www.mowwithus.com"]
    start_urls = ("http://www.mowwithus.com/honda_mowers.html",
                  "http://www.mowwithus.com/honda_electric_lawnmowers.html",
                  "http://www.mowwithus.com/husqvarna_lawn_mowers.html",
                  "http://www.mowwithus.com/john_deere_mowers.html",
                  "http://www.mowwithus.com/masport_mowers.html",
                  "http://www.mowwithus.com/hayter_mowers.html",
                  "http://www.mowwithus.com/enviromower_mowers.html",
                  "http://www.mowwithus.com/atco_mowers.html",
                  "http://www.mowwithus.com/allen_hover_mowers.html",
                  "http://www.mowwithus.com/wolf_mowers.html",
                  "http://www.mowwithus.com/weibang_petrol_lawn_mowers.html",
                  "http://www.mowwithus.com/sanli_mowers.html",
                  "http://www.mowwithus.com/countax_tractors.html",
                  "http://www.mowwithus.com/johndeere_tractors.html",
                  "http://www.mowwithus.com/honda_tractors.html",
                  "http://www.mowwithus.com/snapper_tractors.html",
                  "http://www.mowwithus.com/husqvarna_tractors.html",
                  "http://www.mowwithus.com/murray_tractors.html",
                  "http://www.mowwithus.com/iqs/cpti.196/shredders.html",
                  "http://www.mowwithus.com/iqs/cpti.172/hedgecutters.html",
                  "http://www.mowwithus.com/tgb_quads.html",
                  "http://www.mowwithus.com/iqs/cpti.157/blower_vacuums.html",
                  "http://www.mowwithus.com/iqs/cpti.176/blower_vacuums.html",
                  "http://www.mowwithus.com/iqs/cpti.69/blower_vacuums.html",
                  "http://www.mowwithus.com/iqs/cpti.101/blower_vacuums.html",
                  "http://www.mowwithus.com/iqs/cpti.156/blower_vacuums.html",
                  "http://www.mowwithus.com/iqs/cpti.71/blower_vacuums.html",
                  "http://www.mowwithus.com/iqs/cpti.188/blower_vacuums.html",
                  "http://www.mowwithus.com/iqs/cpti.74/blower_vacuums.html",
                  "http://www.mowwithus.com/iqs/cpti.95/scarifiers.html",
                  "http://www.mowwithus.com/iqs/cpti.113/scarifiers.html",
                  "http://www.mowwithus.com/iqs/cpti.97/scarifiers.html",
                  "http://www.mowwithus.com/iqs/cpti.114/scarifiers.html",
                  "http://www.mowwithus.com/iqs/cpti.150/scarifiers.html",
                  "http://www.mowwithus.com/iqs/cpti.150/scarifiers.html",
                  "http://www.mowwithus.com/iqs/cpti.160/scarifiers.html",
                  "http://www.mowwithus.com/iqs/cpti.198/scarifiers.html",
                  "http://www.mowwithus.com/iqs/cpti.142/shredders.html",
                  "http://www.mowwithus.com/iqs/cpti.49/shredders.html",
                  "http://www.mowwithus.com/iqs/cpti.52/shredders.html",
                  "http://www.mowwithus.com/iqs/cpti.54/shredders.html",
                  "http://www.mowwithus.com/iqs/cpti.55/shredders.html",
                  "http://www.mowwithus.com/iqs/cpti.159/shredders.html",
                  "http://www.mowwithus.com/iqs/cpti.163/line_trimmers.html",
                  "http://www.mowwithus.com/iqs/cpti.179/line_trimmers.html",
                  "http://www.mowwithus.com/iqs/cpti.162/line_trimmers.html",
                  "http://www.mowwithus.com/iqs/cpti.31/line_trimmers.html",
                  "http://www.mowwithus.com/iqs/cpti.158/line_trimmers.html",
                  "http://www.mowwithus.com/iqs/cpti.34/line_trimmers.html",
                  "http://www.mowwithus.com/iqs/cpti.186/line_trimmers.html",
                  "http://www.mowwithus.com/iqs/cpti.183/hedgecutters.html",
                  "http://www.mowwithus.com/iqs/cpti.184/hedgecutters.html",
                  "http://www.mowwithus.com/iqs/cpti.164/hedgecutters.html",
                  "http://www.mowwithus.com/iqs/cpti.177/hedgecutters.html",
                  "http://www.mowwithus.com/iqs/cpti.40/hedgecutters.html",
                  "http://www.mowwithus.com/iqs/cpti.42/hedgecutters.html",
                  "http://www.mowwithus.com/iqs/cpti.44/hedgecutters.html",
                  "http://www.mowwithus.com/iqs/cpti.45/hedgecutters.html",
                  "http://www.mowwithus.com/iqs/cpti.165/hedgecutters.html",
                  "http://www.mowwithus.com/iqs/cpti.187/hedgecutters.html",
                  "http://www.mowwithus.com/iqs/cpti.78/rotovatorsandtillers.html",
                  "http://www.mowwithus.com/iqs/cpti.143/rotovatorsandtillers.html",
                  "http://www.mowwithus.com/iqs/cpti.194/rotovatorsandtillers.html",
                  "http://www.mowwithus.com/iqs/cpti.199/line_trimmers.html",
                  "http://www.mowwithus.com/iqs/cpti.201/line_trimmers.html",
                  )
    
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        content = hxs.select("//table/tbody/tr/td/p/font/strong")
        items = content.select(".//a/@href").extract()
                    
        for item in items:
            yield Request(item, callback=self.parse_item)
            
        content = hxs.select("//table/tbody/tr/td/p")
        items = content.select(".//a/@href").extract()
                    
        for item in items:
            yield Request(item, callback=self.parse_item)            
                        
            
    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)
        
        name = hxs.select("//h1[@class='ItemDetailHeading']/text()").re(r'([a-zA-Z0-9\-\_\.\(\)\&\#\%\@\!\*][a-zA-Z0-9\-\_\.\(\)\&\#\%\@\!\* ]+)')
        
        url = response.url
        price = hxs.select("//font/font/text()").re(r'Price \xa3([\.0-9,]*)')
        
        if name:
            l = ProductLoader(item=Product(), response=response)
            l.add_value('name', name)        
            l.add_value('url', url)
            l.add_value('price', price)
            yield l.load_item()
