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
from scrapy.conf import settings

settings.overrides['REDIRECT_MAX_METAREFRESH_DELAY'] = 0

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class LdMountainCentreSpider(BaseSpider):
    name = 'ldmountaincentre.com'
    allowed_domains = ['ldmountaincentre.com']
    start_urls = ['http://www.ldmountaincentre.com/ski-c26/accessories-c27',
                  'http://www.ldmountaincentre.com/ski-c26/luggage-c46',
                  'http://www.ldmountaincentre.com/ski-c26/clothing-c69',
                  'http://www.ldmountaincentre.com/ski-c26/equipment-c87',
                  'http://www.ldmountaincentre.com/snowboard-c23/luggage-c48',
                  'http://www.ldmountaincentre.com/snowboard-c23/clothing-c71',
                  'http://www.ldmountaincentre.com/snowboard-c23/equipment-c89',
                  'http://www.ldmountaincentre.com/walk-hike-c1/clothing-c2',
                  'http://www.ldmountaincentre.com/walk-hike-c1/footwear-c18',
                  'http://www.ldmountaincentre.com/walk-hike-c1/bags-c44',
                  'http://www.ldmountaincentre.com/walk-hike-c1/equipment-c77',
                  'http://www.ldmountaincentre.com/camping-c13/sleeping-c56',
                  'http://www.ldmountaincentre.com/camping-c13/tents-c93',
                  'http://www.ldmountaincentre.com/climbing-c4/equipment-c5',
                  'http://www.ldmountaincentre.com/climbing-c4/footwear-c63']

    def __init__(self, *a, **kw):
        super(LdMountainCentreSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
    
    def spider_closed(self, spider):
        if spider.name == self.name:
            shutil.copy('data/%s_products.csv' % spider.crawl_id, os.path.join(HERE, 'product_skus.csv'))
            log.msg("CSV is copied")
    
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//*[@id="categories"]/div/div/a/@href').extract()
        for category in categories:
            url = urljoin_rfc(get_base_url(response), category)
            yield Request(url+'?show=all', callback=self.parse_products)
   
    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//*[@id="search_results_products"]/div')
        for product in products:
            loader = ProductLoader(item=Product(), response=response)
            relative_url =  ''.join(product.select('div/p/a[@class="product_options_view"]/@href').extract())
            url = urljoin_rfc(get_base_url(response), relative_url)
            loader.add_value('sku', url.split('-p')[-1])
            name = ''.join(product.select('div/div[@class="product_title"]/descendant::text()').extract()).strip().replace('  ',' ')
            loader.add_value('name', name)
            loader.add_value('url', url)
            price = product.select('div/div/div/span/span[@class="price"]/span[@class="inc"]/span[@class="GBP"]/text()').extract()
            if price:
                price = price[0]
            else:
                price = 0
            loader.add_value('price', price)
            yield loader.load_item()
        next = hxs.select('//a[@class="next_page page_num"]/@href').extract()
        if next:
            yield Request(next[-1])
        
