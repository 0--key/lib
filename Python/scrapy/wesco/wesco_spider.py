import csv
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader


HERE = os.path.abspath(os.path.dirname(__file__))

class CBCDirectSpider(BaseSpider):
    name = 'cbcdirect.com'
    allowed_domains = ['cbcdirect.com']

    def start_requests(self):
        with open(os.path.join(HERE, 'products.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = 'http://www.cbcdirect.com/direct/Search/SearchResults.aspx?\
advSearch=1&searchFlag=2&partNoKeyword=simus&partNoKeywordValue=%s\
&searchAll=1&stringPos=1&yourCat=0&paperCatalog=1&gr=0&sortfield=simus&sortDirection=asc'

                yield Request(url % row['UPC'], meta={'sku': row['Part #']})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        name = hxs.select('//span[@id="ProductDetail1_lblDescription"]//text()').extract()
        if name:
            loader = ProductLoader(item=Product(), response=response)
            loader.add_value('name', name)
            loader.add_value('url', response.url)
            loader.add_xpath('price', '//*[@class="yourPriceText"]//text()')
            loader.add_value('sku', response.meta['sku'])
            yield loader.load_item()
