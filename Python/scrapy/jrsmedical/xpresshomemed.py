import os
import csv
import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class XpressHomeMedSpider(BaseSpider):
    name = 'xpresshomemed.com'
    allowed_domains = ['xpresshomemed.com']
    start_urls = ()

    def start_requests(self):
        with open(os.path.join(HERE, 'jrsmedical_products.csv')) as f:
            reader = csv.reader(f)
            reader.next()
            reader = set([row[1] for row in reader])
            url = 'http://www.xpresshomemed.com/SearchResults.asp?Search=%s'
            for row in reader:
                sku = row
                if url:
                    yield Request(url % re.sub(' ', '+', sku)[3:], meta={'sku': sku}, dont_filter=True)


    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # next_page = hxs.select(u'').extract()

        # if next_page:
            # yield Request(urljoin_rfc(base_url, next_page[0]), meta=response.meta)

        products = hxs.select(u'//td//a[child::big or contains(@class,"productnamecolor")]/@href').extract()
        for url in products:
            url = urljoin_rfc(base_url, url)
            yield Request(url, callback=self.parse_product, meta=response.meta, dont_filter=True)
        if not products:
            try:
                for product in self.parse_product(response):
                    yield product
            except TypeError:
                pass

    def parse_product(self, response):
        base_url = get_base_url(response)
        search_sku = response.meta['sku']
        hxs = HtmlXPathSelector(response)

        loader = ProductLoader(item=Product(), response=response)
        loader.add_value('url', response.url)
        name_xpaths = [u'//font[contains(@class,"productname")]/big/text()',
                       u'//font[contains(@class,"productname")]/text()']
        for name_xpath in name_xpaths:
            main_name = hxs.select(name_xpath).extract()
            if main_name:
                main_name = main_name[0].strip()
                break
        if not main_name:
            main_name = response.url
            main_name = re.search(u'.*/(.*)\.htm', main_name)
            if main_name:
                main_name = main_name.groups()[0] + u' (%s)' % search_sku
        options =  hxs.select(u'//td//text()').re(u'PURCHASE OPTIONS: (.*)')
        if options:
            main_name += u' %s' % options[0].strip()
        loader.add_value('name', main_name)
        loader.add_xpath('price', u'//td//font[contains(@class,"pricecolor") and not(ancestor::table[contains(@id,"related")])]/text()')
        loader.add_value('sku', search_sku)

        sku = hxs.select(u'//span[@class="product_code"]/text()').extract()
        if sku:
            sku = re.sub('-', '', sku[0])
            if sku.startswith(search_sku):
                yield loader.load_item()