import re
import os
import csv
import hashlib
import re

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode
from product_spiders.items import Product, ProductLoaderWithNameStrip\
                             as ProductLoader
from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))


class DiscountedHeatingSpider(CrawlSpider):

    name = 'discountedheating.co.uk'
    allowed_domains = ['www.discountedheating.co.uk', 'discountedheating.co.uk']
    start_urls = ('http://www.discountedheating.co.uk/index.php?route=product/search&filter_name=&filter_sub_category=true?limit=2000',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="product-list"]/div')
        
        # New site structure?
        if not products:
            yield Request('http://www.discountedheating.co.uk/shop/acatalog/index.html', self.parse_stuff)
        
        for product in products:
            name = product.select('div[@class="name"]/a/text()').extract()
            price = ''.join(product.select('div[@class="price"]/span/text()').extract()).split(':')[-1]
            url = product.select('div[@class="name"]/a/@href').extract()[0]
            yield Request(url, callback=self.parse_product, meta={'name':name, 'price':price})
        next = hxs.select('//div[@class="pagination"]/div/a[text()=">"]/@href').extract()
        if next:
            yield Request(next[0])

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        loader = ProductLoader(item=Product(), response=response)
        loader.add_value('name', response.meta['name'])
        loader.add_value('price', response.meta['price'])
        loader.add_value('url', response.url)
        mpn = hxs.select('//*[@id="tab-attribute"]/table/tbody/tr[td/text()="Manufacturers Part No"]/td/text()').extract()
        sku = hxs.select('//*[@id="tab-attribute"]/table/tbody/tr[td/text()="Act Ref"]/td/text()').extract()
        if sku:
            loader.add_value('identifier', sku[1])
            loader.add_value('sku', sku[1]) 
        else:
            if mpn:
                loader.add_value('identifier', mpn[1])
                loader.add_value('sku', mpn[1])
        yield loader.load_item()

    def parse_stuff(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)
        
        categories = hxs.select('//div[@id="main"]//div[contains(@class,"act_sec_border")]/a/@href').extract()
        for category in categories:
            yield Request(urljoin_rfc(base_url, category), callback=self.parse_stuff) 
    
        products = hxs.select('//div[@id="main"]//form[descendant::input[@name="PAGE" and @value="PRODUCT"]]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            sku = item.select('.//span[@itemprop="identifier"]/text()').extract()[0]
            loader.add_value('sku', sku)
            loader.add_xpath('name', './/span[@itemprop="name"]/text()')
            loader.add_xpath('price', './/span[@class="pricestyle"]/text()')
            url = product.select('.//a[contains(@href,".html")]/@href').extract()
            if url:
                loader.add_value('url', urljoin_rfc(base_url, url[0]))
            else:
                loader.add_value('url', '%s#%s' % (response.url, sku))
            yield loader.load_item()