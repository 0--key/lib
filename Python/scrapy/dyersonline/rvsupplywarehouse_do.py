import os
import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy import log

import csv, codecs, cStringIO

from productloader import load_product
from scrapy.http import FormRequest

HERE = os.path.abspath(os.path.dirname(__file__))
CSV_FILENAME = os.path.join(os.path.dirname(__file__), 'rvsupply.csv')

class rvsupplywarehouseDOSpider(BaseSpider):
    name = 'rvsupplywarehouse.com_DO'
    allowed_domains = ['www.rvsupplywarehouse.com', 'rvsupplywarehouse.com']
    start_urls = ('http://www.rvsupplywarehouse.com/c/30',)

    def __init__(self, *args, **kwargs):
            super(rvsupplywarehouseDOSpider, self).__init__(*args, **kwargs)
            self.names = {}
            with open(CSV_FILENAME) as f:
               reader = csv.DictReader(f)
               for row in reader:
                   self.names[row['url']] = row['name'].decode('utf-8', 'ignore')

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
                    return
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        # pagination
        next_pages = hxs.select(u'//div[@class="pager"]/a/@href').extract()
        for next_page in next_pages:
            next_page = urljoin_rfc(get_base_url(response), next_page)
            yield Request(next_page)

        # catalogs
        catalogs = hxs.select(u'//div[@class="listbox"]/ul/li/a/@href').extract()
        for catalog in catalogs:
            yield Request(urljoin_rfc(base_url,catalog)) 
            
        # products
        products = hxs.select(u'//div[@class="product-item"]/div[@class="description"]/a/@href').extract()
        for product in products:
            product = urljoin_rfc(get_base_url(response), product)
            yield Request(product, callback=self.parse_product)
    
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        res = {}
        hxs = HtmlXPathSelector(response)
        

        res['url'] = response.url
        name = hxs.select('//div[@class="productname"]//text()').extract()[0].strip()
        price = hxs.select('//span[@class="productPrice"]/span/text()').extract()[0]
        if price:
            res['description'] = self.names.get(response.url, name)
            res['price'] = price
            yield load_product(res, response)
        else:
            return

            
            
        
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
