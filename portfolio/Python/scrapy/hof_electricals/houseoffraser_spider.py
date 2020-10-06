import os
import shutil
from scrapy import signals
from scrapy import log
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url
from scrapy.xlib.pydispatch import dispatcher

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class HouseOfFraserSpider(BaseSpider):
    name = 'houseoffraser.co.uk-electricals'
    allowed_domains = ['houseoffraser.co.uk', 'houseoffraserkitchenappliances.co.uk']
    start_urls = ['http://www.houseoffraser.co.uk/Electricals/10,default,sc.html']

    def __init__(self, *a, **kw):
        super(HouseOfFraserSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
    
    def spider_closed(self, spider):
        if spider.name == self.name:
            shutil.copy('data/%s_products.csv' % spider.crawl_id, os.path.join(HERE, 'houseoffraser_electricals.csv'))
            log.msg("CSV is copied")

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories =  hxs.select('//*[@id="categoryQuickLinks"]/div/ul/li/a[text()!="SALE"]/@href').extract()
        if categories:
            for category in categories:
                url =  urljoin_rfc(get_base_url(response), category)
                yield Request(url, callback=self.parse_product)
        

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="mainColumn"]/ol[@class="productListing clearfix"]/li')
        if products:
            for product in products:
                loader = ProductLoader(item=Product(), selector=product)
                name = ' '.join(product.select('span[@class="productInfo"]/a/descendant::*/text()').extract())
                loader.add_value('name', name)
                loader.add_xpath('url', 'a/@href')
                loader.add_xpath('price', 'span/span[@class="price" or @class="priceNow"]/text()')
                yield loader.load_item()
            next = hxs.select('//a[@class="pager nextPage"]/@href').extract()
            if next:
                yield Request(next[0], callback=self.parse_product)
        else:
            sub_categories = hxs.select('//ol[@class="interstitialMenu clearfix"]/li/a/@href').extract() 
            if sub_categories:
                for sub_category in sub_categories:
                    url =  urljoin_rfc(get_base_url(response), sub_category)
                    yield Request(url, callback=self.parse_product)
            else:
                categories = hxs.select('//*[@id="container"]/div[@class="rollovers"]/div/a/@href').extract()
                for category in categories:
                    yield Request(category, callback=self.parse_size_products)

    def parse_size_products(self, response):
        hxs = HtmlXPathSelector(response)
        size = hxs.select('//ul[@class="pageSize"]/li/a/@href').extract()
        if size:
            size = size[0].split('&')[-1]
            yield Request(''.join((response.url,'&',size)), callback=self.parse_kitchen_products)
    
    def parse_kitchen_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//*[@id="content"]/div[@id!="pageControl"]/div/ul')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', 'li/a/strong/text()')
            url = product.select('li[@class="alignCenter"]/a/@href').extract()
            if url:
                url =  urljoin_rfc(get_base_url(response), url[0])
            loader.add_value('url', url)
            loader.add_xpath('price','div[@class="priceBox"]/strong/a/text()')
            yield loader.load_item()
        
