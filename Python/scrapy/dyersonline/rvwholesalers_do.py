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

class rvwholesalersDOSpider(BaseSpider):
    name = 'rvwholesalers.com_DO'
    allowed_domains = ['www.rvwholesalers.com','rvwholesalers.com']
    start_urls = ('http://rvwholesalers.com',)

    def __init__(self, *args, **kwargs):
        super(rvwholesalersDOSpider, self).__init__(*args, **kwargs)
        self.URLBASE = 'http://rvwholesalers.com/'

        # parse the csv file to get the product ids
        self.csv_file = UnicodeReader(open(os.path.join(HERE, 'skus.csv')))

    def start_requests(self):
        for row in self.csv_file:
            url = self.URLBASE + 'catalog/_search.php?page=1&q=' + row[2]
            request = Request(url,callback=self.parse_product)
            request.meta['sku'] = row[0]
            request.meta['search_q'] = row[2]
            yield request
        yield Request('http://rvwholesalers.com/catalog/',self.parse)
        
    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        res = {}
        
        cats = hxs.select('//div[@id="my_menu"]//a/@href').extract()
        for cat in cats:
            request = Request(urljoin_rfc(base_url,cat), callback=self.parse)
            yield request   
            
        subcats = hxs.select('//td[@class="SubcatTitle"]/a/@href').extract()
        for scat in subcats:
            request = Request(urljoin_rfc(base_url,scat), callback=self.parse)      
            yield request   
            
        pages = hxs.select('//td[@class="NavigationCell"]/a/@href').extract()
        for page in pages:
            request = Request(urljoin_rfc(base_url,page), callback=self.parse)
            yield request     
            
        products = hxs.select('//td[@class="PListCell"]')
        for product in products:
            url = response.url
            name = product.select("./a[@class='ProductTitle']/text()").extract()
            if name:
                price = "".join(product.select('./font[@class="ProductPrice"]/span/text()').re(r'([0-9\,\. ]+)')).strip()
                url = product.select("./a[@class='ProductTitle']/@href").extract()
                res['url'] = urljoin_rfc(base_url,url[0])
                res['description'] = name[0].strip()
                res['price'] = price
                yield load_product(res, response)              

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        res = {}
        
        products = hxs.select('//td[@class="PListCell"]')
        for product in products:
            sku_ = product.select("./text()[contains(.,'" + response.meta['search_q'] + "')]").extract()
        
            if sku_:
                url = response.url
                name = product.select("./a[@class='ProductTitle']/text()").extract()
                if name:
                    price = "".join(product.select('./font[@class="ProductPrice"]/span/text()').re(r'([0-9\,\. ]+)')).strip()
                    url = product.select("./a[@class='ProductTitle']/@href").extract()
                    res['url'] = urljoin_rfc(base_url,url[0])
                    res['description'] = name[0].strip()
                    res['price'] = price
                    if 'sku' in responce.meta:
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
