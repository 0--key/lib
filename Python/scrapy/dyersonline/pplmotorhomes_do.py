import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc
from scrapy import log

import csv, codecs, cStringIO

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class PplmotorhomesDOSpider(BaseSpider):
    USER_AGENT = "Googlebot/2.1 ( http://www.google.com/bot.html)"
    name = 'pplmotorhomes.com_DO'
    allowed_domains = ['www.pplmotorhomes.com','pplmotorhomes.com','google.com','www.google.com']
    start_urls = ('http://www.google.com',)

    def __init__(self, *args, **kwargs):
        super(PplmotorhomesDOSpider, self).__init__(*args, **kwargs)
        # parse the csv file to get the product ids
        self.csv_file = UnicodeReader(open(os.path.join(HERE, 'skus.csv')))

    def start_requests(self):
        for row in self.csv_file:
            if row[1] != '0':
                url = 'http://www.google.com/cse?cx=008536649155685395941%3Aiahjfr-bdbs&ie=UTF-8&q='+row[1]+'&sa=Search&siteurl=www.pplmotorhomes.com&ref=www.pplmotorhomes.com&nojs=1'
                request = Request(url,callback=self.parse)
                request.meta['sku'] = row[0]
                request.meta['search_q'] = row[1]
                yield request         

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)
        product_urls = hxs.select('//a[@class="l"]/@href').extract()
        #product_urls = hxs.select('//a[@class="gs-title"]/@href').extract()
        #log.msg("CRAWLING:::::::::::  %s" % hxs.select('/html').extract())
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
        hxs = HtmlXPathSelector(response)
        
        products = hxs.select('//table[@width="86%"]/tr')
        for product in products:
            
            sku_ = product.select('./form/td[1]/b/text()').extract()
            if sku_:
              if sku_[0] == response.meta['search_q']:
                price = "".join(product.select("./form/td[3]/font/b/text()").re(r'([0-9\,\. ]+)')).strip()
                if price:
                    name = product.select('./form/td[2]/text()').extract()[0]
                    product_loader = ProductLoader(item=Product(), response=response)
                    product_loader.add_value('price', price)
                    product_loader.add_value('url', response.url)
                    product_loader.add_value('sku', response.meta['sku'])
                    product_loader.add_value('name', name)
                    return product_loader.load_item()
                   

        
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
