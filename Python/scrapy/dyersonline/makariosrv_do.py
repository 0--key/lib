import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy import log

import csv, codecs, cStringIO

from productloader import load_product
from scrapy.http import FormRequest

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class makariosrvDOSpider(BaseSpider):
    name = 'makariosrv.com_DO'
    allowed_domains = ['www.makariosrv.com','makariosrv.com']
    start_urls = ('http://makariosrv.com',)

    def __init__(self, *args, **kwargs):
        super(makariosrvDOSpider, self).__init__(*args, **kwargs)
        self.URLBASE = 'http://makariosrv.com/'

        # parse the csv file to get the product ids
        self.csv_file = UnicodeReader(open(os.path.join(HERE, 'skus.csv')))

    def start_requests(self):
        for row in self.csv_file:
            url = self.URLBASE + 'search.php?search_query=' + row[2] + '&x=28&y=13'
            request = Request(url,callback=self.parse_search)
            request.meta['sku'] = row[0]
            request.meta['search_q'] = row[2]
            yield request
        yield Request('http://www.makariosrv.com/',self.parse)            
        
        
        
    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        
        cats = hxs.select('//div[@class="SideCategoryListFlyout"]//li/a/@href').extract()
        for cat in cats:
            request = Request(urljoin_rfc(base_url,cat), callback=self.parse)
            yield request           
        
        product_urls = hxs.select('//ul[contains(@class,"ProductList")]/li/div[contains(@class,"ProductImage")]/a/@href').extract()
        for product in product_urls:
            request = Request(product, callback=self.parse_product)
            yield request
      

    def parse_search(self, response):
        if not isinstance(response, HtmlResponse):
            return
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        
        product_urls = hxs.select('//ul[contains(@class,"ProductList")]/li/div[@class="ProductImage"]/a/@href').extract()
        if product_urls:
            request = Request(product_urls[0], callback=self.parse_product)
            request.meta['sku'] = response.meta['sku']
            request.meta['search_q'] = response.meta['search_q']
            yield request
        else:
            return



    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        res = {}
        
        url = response.url
        name = hxs.select("//div[contains(@class,'BlockContent')]/h1/text()").extract()
        if name:
            price = "".join(hxs.select('//em[@class="ProductPrice VariationProductPrice"]/span[@class="SalePrice"]/text()').re(r'([0-9\,\. ]+)')).strip()
            if not price:
                price = "".join(hxs.select('//em[@class="ProductPrice VariationProductPrice"]/text()').re(r'([0-9\,\. ]+)')).strip()
            res['url'] = url
            res['description'] =   name[0].strip()
            res['price'] = price
            if 'sku' in response.meta:
                res['sku'] = response.meta['sku']
            yield load_product(res, response)
     

        
class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
