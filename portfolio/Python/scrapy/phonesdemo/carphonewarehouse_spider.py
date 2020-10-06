from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc
from scrapy import log
from urlparse import urlparse
from urlparse import parse_qs
import time
import json

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader


class CarphoneWarehouseSpider(BaseSpider):
    name = 'carphonewarehouse.com'
    allowed_domains = ['carphonewarehouse.com']
    start_urls = ['http://www.carphonewarehouse.com/pay-as-you-go/shopbybrand']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        # Only URL with "/pay-as-you-go/" and has "manufacturer=" in the query
        categories = hxs.select('//map[@name="Mapre"]/area[contains(@href,"/pay-as-you-go/") and contains(@href,"manufacturer=")]/@href').extract()
        for category in categories:
            url = urljoin_rfc(response.url, category, response.encoding)
            yield Request(url, callback=self.parse_cat)

    def parse_cat(self, response):
        hxs = HtmlXPathSelector(response)
        
        # Somehow the API need the manufacturer name, here is the mapping from one of their JS file
        manufactureMap = { 'BLA030': 'BlackBerry',
            'ALC001': 'Alcatel',
            'HTC001': 'HTC','LGE001':'LG Electronics','MOT001':'Motorola','NOK001':'Nokia','SAM001':'Samsung','ERI001':'Sony Ericsson',
            'DEL004':'Dell','APP002':'Apple','apple-iphone4':'Apple','DOR006':'Doro','JCB001':'JCB','SON004':'Sony','VOD008':'Vodafone',
            'PAN001':'Panasonic'
           }
        
        # Parse URL
        o = urlparse(response.url)
        # Parse query
        query = parse_qs(o.query)
        # Get manufacturer code
        man_code = query['manufacturer'][0]
        man_str = manufactureMap[man_code]
            
        # Enter manufacturer code & name
        facets = {"dt":"pg","fp":"paygsfphonefinder","mo":"PHONES","sort":"ms desc,pc asc,tp asc,mn asc","ma":man_code,"pb":man_str}
        # Get products from some sort of Solr API
        url = "http://www.carphonewarehouse.com/solrSearch.do?_=%d&facets=%s" % (int(time.time()), json.dumps(facets))
        yield Request(url, callback=self.parse_solr)
        
    def parse_solr(self, response):
        # Response body is in JSON
        result = json.loads(response.body)
        items = result['grouped']['mn']['groups']
        
        for item in items:
            detail = item['doclist']['docs'][0]
            sku = detail['mc']
            url = 'http://www.carphonewarehouse.com/mobiles/mobile-phones/%s/PPAY' % sku 
            price = detail['pc']
            name = detail['mn']
            loader = ProductLoader(item=Product(), response=response)
            loader.add_value('url', url)
            loader.add_value('sku', sku)
            loader.add_value('name', name)
            loader.add_value('price', price)
            yield loader.load_item()
    
