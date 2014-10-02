import re
import functools

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.log import msg

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from sutils import comas2dots, first

# TODO: categories_nextpage_xpath
# TODO: create parent spider class


class CariboomSpider(BaseSpider):
   
    name = 'cariboom.com'
    allowed_domains = [name]
    start_urls = ('http://www.cariboom.com',)
   
    categories_xpath = "//div[@id='custommenu']//a/@href"
    categories_nextpage_xpath = None
    products_xpath = "//div[@class='category-products']/ol/li"
    products_nextpage_xpath = "//*[@id='contenu']/div[2]/div[2]/div/ol/li[3]/@onclick"
    products_nextpage_re = "='(.+)'"
    
    product_name = ("./div[@class='title']/h2/a/text()", )
    product_price = ("./div[@class='prix_sans_promo']/div[@class='prix_vente_sans_promo']/text()",
                     "./div[@class='prix']/div[@class='prix_vente']/text()",)
    product_url = ("./div[@class='title']/h2/a/@href", )
    
    
    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        if self.categories_xpath:
            categories = hxs.select(self.categories_xpath).extract()
            for url in categories:
                yield Request(urljoin_rfc(base_url, url),
                              callback=self.parse_page)


    def parse_page(self, response):
        base_url = get_base_url(response)
        base_url_func = functools.partial(urljoin_rfc, base_url)
        hxs = HtmlXPathSelector(response)
        
        # products next page
        if self.products_nextpage_xpath:
            if not self.products_nextpage_re:
                url = hxs.select(self.products_nextpage_xpath).extract()
            else:
                url = hxs.select(self.products_nextpage_xpath).re(
                                        self.products_nextpage_re)
            if url:
                yield Request(urljoin_rfc(base_url, url[0]),
                        callback=self.parse_page)
            
        # products
        if self.products_xpath:
            for z in hxs.select(self.products_xpath):
                loader = ProductLoader(selector=z, item=Product())
                if self.product_name:
                    for xpath in self.product_name:
                        loader.add_xpath('name', xpath)
                #loader.add_xpath('name', "./div[@class='margue']/text()")
                if self.product_url:
                    for xpath in self.product_url:
                        loader.add_xpath('url', xpath, first, base_url_func)
                if self.product_price:
                    for xpath in self.product_price:
                        loader.add_xpath('price', xpath, comas2dots)

                yield loader.load_item()
    
