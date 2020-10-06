import csv
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader


HERE = os.path.abspath(os.path.dirname(__file__))

class GraingerSpider(BaseSpider):
    name = 'wesco-grainger.com'
    allowed_domains = ['grainger.com']
    start_urls = ('http://www.newark.com/jsp/search/advancedsearch.jsp',)

    def start_requests(self):
        with open(os.path.join(HERE, 'products.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                sku = row['Part #']
                url = 'http://www.grainger.com/Grainger/wwg/search.shtml?'+\
                      'searchQuery=%(sku)s&op=search&Ntt=%(sku)s&N=0&sst=subset'

                yield Request(url % {'sku': sku}, meta={'sku': sku})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        if hxs.select('//div[@id="noResultsMsg"]') \
           or not hxs.select('//td[text()="Mfr. Model #"]/following-sibling::td/text()'):
            return

        loader = ProductLoader(item=Product(), response=response)
        loader.add_xpath('name', '//div[@id="PageTitle"]/h1//text()')
        loader.add_value('url', response.url)
        loader.add_xpath('price', '//td[@class="tdrightalign"]/strong[starts-with(text(), "$")]/text()')
        loader.add_xpath('sku', '//td[text()="Mfr. Model #"]/following-sibling::td/text()')
        sku = loader.get_output_value('sku')
        if sku.lower() != response.meta['sku'].lower():
            return

        yield loader.load_item()
