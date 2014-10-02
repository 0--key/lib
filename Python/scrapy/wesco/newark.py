import csv
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader


HERE = os.path.abspath(os.path.dirname(__file__))

class NewarkSpider(BaseSpider):
    name = 'newark.com'
    allowed_domains = ['newark.com']
    start_urls = ('http://www.newark.com/jsp/search/advancedsearch.jsp',)

    def parse(self, response):
        with open(os.path.join(HERE, 'products.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                sku = row['Part #']
                yield FormRequest.from_response(response, formname='advancedsearch',
                    formdata={'/pf/search/AdvancedSearchFormHandler.partNumberMatchMode': '3',
                              'partNumber': sku}, meta={'sku': sku}, callback=self.parse_product)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        if hxs.select('//span[@id="totalNoResultsSlotAtTop"]'):
            return

        loader = ProductLoader(item=Product(), response=response)
        loader.add_xpath('name', '//div[@id="headerContainer"]/h1/text()')
        loader.add_value('url', response.url)
        loader.add_xpath('price', '//span[contains(@class, "mfProductDescriptionAndPrice")]/text()')
        loader.add_xpath('sku', '//dt[text()="Manufacturer Part No:"]/following-sibling::dd/text()')
        sku = loader.get_output_value('sku')
        if sku.lower() != response.meta['sku'].lower():
            return

        yield loader.load_item()

