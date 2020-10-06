import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

import csv, codecs, cStringIO

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class AdventureRVDOSpider(BaseSpider):
    name = 'adventurerv.net_DO'
    allowed_domains = ['www.adventurerv.net']
    start_urls = ('http://www.adventurerv.net/',)

    def __init__(self, *args, **kwargs):
        super(AdventureRVDOSpider, self).__init__(*args, **kwargs)
        self.URLBASE = 'http://www.adventurerv.net/'

        # parse the csv file to get the product ids
        self.csv_file = UnicodeReader(open(os.path.join(HERE, 'skus.csv')))

    def start_requests(self):
        for row in self.csv_file:
            url = self.URLBASE + 'advanced_search_result.php?keywords=' + row[1]
            request = Request(url,callback=self.parse_product)
            request.meta['sku'] = row[0]
            yield request
        yield Request('http://www.adventurerv.net/advanced_search_result.php?keywords=%25',self.parse)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        
        pages = hxs.select('//a[@title=" Next Page "]/@href').extract()
        for page in pages:
            request = Request(urljoin_rfc(base_url,page), callback=self.parse)
            yield request            
        
        products = hxs.select('//div[@class="product-listing"]/a/@href').extract()
        for product in products:
            request = Request(urljoin_rfc(base_url,product), callback=self.parse_product)
            yield request     
            
        products = hxs.select('//div[@class="product-listing-odd"]/a/@href').extract()
        for product in products:
            request = Request(urljoin_rfc(base_url,product), callback=self.parse_product)
            yield request                 
        
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)
        price = hxs.select('//div[@class="h3"]/span[@class="productSpecialPrice"]/text()')
        if not price:
            price = hxs.select('//div[@class="h3"]/text()')
        
        if price:
            name = hxs.select('//div[@id="content"]/div[@id="right-column"]/h1[@class="bottom-border"]/text()').extract()[0]
            product_loader = ProductLoader(item=Product(), response=response)
            product_loader.add_xpath('price', '//div[@class="h3"]/span[@class="productSpecialPrice"]/text()',
                                     re='.*\$(.*)')
            product_loader.add_xpath('price', '//div[@class="h3"]/text()', re='.*\$(.*[0-9])')
            product_loader.add_value('url', response.url)
            if 'sku' in response.meta:
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
