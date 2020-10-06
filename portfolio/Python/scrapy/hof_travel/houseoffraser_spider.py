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
    name = 'houseoffraser.co.uk-travel'
    allowed_domains = ['houseoffraser.co.uk']
    start_urls = ['http://www.houseoffraser.co.uk/Antler+Bags+Luggage/BRAND_ANTLER_17,default,sc.html&redirectQuery=antler?sz=200&spcl',
                  'http://www.houseoffraser.co.uk/Samsonite+Bags+Luggage/%20BRAND_SAMSONITE_17,default,sc.html&redirectQuery=samsonite?sz=200&spcl',
                  'http://www.houseoffraser.co.uk/Eastpak+Bags+Luggage/BRAND_EASTPAK_17,default,sc.html?sz=200&spcl',
                  'http://www.houseoffraser.co.uk/Wenger/BRAND_WENGER,default,sc.html?redirectQuery=wenger?sz=200&spcl']

    def __init__(self, *a, **kw):
        super(HouseOfFraserSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        if spider.name == self.name:
            shutil.copy('data/%s_products.csv' % spider.crawl_id, os.path.join(HERE, 'houseoffraser_travel.csv'))
            log.msg("CSV is copied")

    def parse(self, response):
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
