import re
import functools

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.log import msg

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
#from product_spiders.utils import extract_price

#HERE = os.path.dirname(os.path.abspath(__file__))

from sutils import comas2dots, first
from scrapy import log

class NaturabuySpider(BaseSpider):
   
    name = 'naturabuy.fr'
    allowed_domains = [name]
    start_urls = ('http://www.naturabuy.fr',)
   
    categories_xpath = "//*[@id='homelcats']/h2/a/@href"
    products_xpath = "//div[@class='storeitem_price']/.."
    products_nextpage_xpath = "//a[@id='suiv']/@href"
    
    
    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        if self.categories_xpath:
            #categories = hxs.select(self.categories_xpath).extract()
            categories = ['http://www.naturabuy.fr/Chaussures-bottes-cat-16.html',
                          'http://www.naturabuy.fr/Optiques-Lunettes-Jumelles-cat-559.html',
                          'http://www.naturabuy.fr/Vetements-Chasse-Peche-Tir-cat-1.html']
            for url in categories:
                yield Request(urljoin_rfc(base_url, url) + "?SortProperty=min_bid&listall=1&sortpromo=percent", callback=self.parse_page)
                

    def parse_page(self, response):
        base_url = get_base_url(response)
        base_url_func = functools.partial(urljoin_rfc, base_url)
        hxs = HtmlXPathSelector(response)
        
        # next page
        if self.products_nextpage_xpath:
            url = hxs.select(self.products_nextpage_xpath).extract()
            if url:
                yield Request(urljoin_rfc(base_url, url[0]), callback=self.parse_page)
            
        # products
        i = 0
        if self.products_xpath:
            for z in hxs.select(self.products_xpath)[1:]:
                #name = z.select(".//div[@class='detailsInnerWrap']/a[@class='name']/text()").extract()
                loader = ProductLoader(selector=z, item=Product())
                loader.add_xpath('price', ".//div[@class='storeitem_price']/span[@class='storeitem_firstprice']/text()", comas2dots)
                loader.add_xpath('identifier', "./div/a/@href", first, re="\-(\d+)\.html")
                loader.add_xpath('sku', "./div/a/@href", first, re="\-(\d+)\.html")
                loader.add_xpath('url', "./div/a/@href", first, base_url_func)
                #loader.add_xpath('url', "./div[@class='storeitem_title store_bolded']/a/@href", first, base_url_func)
                loader.add_xpath('name', "./div/a/b/text()")
                #loader.add_xpath('name', "./div[@class='storeitem_title store_bolded']/a/text()")
                loader.add_xpath('name', "./div/a/text()")

                yield loader.load_item()
                i += 1

        if i != 30:
            log.msg("Less than 30 products in %s %s" % (response.url, i))

        
