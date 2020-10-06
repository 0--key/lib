import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy import log
from urlparse import urlparse
import time
from scrapy.http import FormRequest

class CoralReefAquaticsSpider(BaseSpider):
    name = 'coralreefaquatics.co.uk'
    allowed_domains = ['www.coralreefaquatics.co.uk']
    start_urls = (
                  'http://www.coralreefaquatics.co.uk/',
                  )
    
    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        
        cat_urls = hxs.select('//ul[@class="fl_menu"]/li[contains(@id,"store")]/a/@href').extract()
        for url in cat_urls:
            yield Request(urljoin_rfc(base_url, url), callback=self.parse_cat)
    
    def parse_cat(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        
        subcat_urls = hxs.select('//div[@class="productsubcats"]//a[contains(@href,"store/category")]/@href').extract()
        if subcat_urls:
            for url in subcat_urls:
                yield Request(urljoin_rfc(base_url, url), callback=self.parse_cat)
        
        products = hxs.select('//a[contains(@href,"store/product")]/@href').extract()
        if products:
            for url in products:
                yield Request(urljoin_rfc(base_url, url), callback=self.parse_product)
        
    def parse_product(self, response): 
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        
        # Is this a product with many option/attributes?
        options = hxs.select('//select[@name="selection[]"]/option')
        if options:
            log.msg('Found %d options for this product' % len(options))
            url = urljoin_rfc(base_url, 'cmsplus/store-stockcheck.php')
            # Post these parameters
            prodid = hxs.select('//input[@name="prodid"]/@value').extract()[0]
            versionids = hxs.select('//input[@name="verids"]/@value').extract()[0]
            presel = hxs.select('//input[@name="presel"]/@value').extract()[0]
            curtime = "%s" % int(round(time.time()*1000))
            name = hxs.select('//h1/text()').extract()[0]
            sku = hxs.select('//input[@name="prodid"]/@value').extract()[0]
            
            for option in options:
                loader = ProductLoader(item=Product(), response=response)
                loader.add_value('url', response.url)
                #loader.add_xpath('price', '//span[@id="ourprice"]/text()')
                sku_sub = option.select('@value').extract()[0]
                loader.add_value('sku', '%s_%s' % (sku, sku_sub))
                loader.add_value('name', '%s Type: %s' % (name, option.select('text()').extract()[0]))
                request = FormRequest(url=url,
                        formdata={'prodid': prodid, 'versionids': versionids, 'presel': presel, 'var[]':sku_sub, 'firstrun': '1', 'curtime': curtime},
                        callback=self.parse_product_price)
                request.meta['item'] = loader
                yield request
                
        else:
            loader = ProductLoader(item=Product(), response=response)
            loader.add_value('url', response.url)
            loader.add_xpath('sku', '//input[@name="prodid"]/@value')
            loader.add_xpath('name', '//h1/text()')
            loader.add_xpath('price', '//span[@id="ourprice"]/text()')
            yield loader.load_item()
            
        #request = Request(url, callback=parse_product_price)
        #request.meta['item'] = loader
        #yield request
        #yield loader.load_item()
        
    def parse_product_price(self, response):
        price_re = re.compile("price=(\d+(?:\.\d+))")
        match = price_re.search(response.body)
        
        if match:
            log.msg('Got price: %s' % match.group(1))
            loader = response.meta['item']
            loader.add_value('price', match.group(1))
            yield loader.load_item()
        else:
            log.msg('Invalid response: %s' % response.body)
        