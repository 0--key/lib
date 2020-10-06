import os
from decimal import Decimal
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy import log

import csv, codecs, cStringIO

from productloader import load_product
from product_spiders.items import Product
from scrapy.http import FormRequest

HERE = os.path.abspath(os.path.dirname(__file__))

class AmericanrvDOSpider(BaseSpider):
    name = 'americanrvcompany.com_DO'
    allowed_domains = ['www.americanrvcompany.com', 'americanrvcompany.com']
    start_urls = ('http://www.americanrvcompany.com/search.asp?keyword=%25%25&search.x=49&search.y=39',)

    def __init__(self, *args, **kwargs):
        super(AmericanrvDOSpider, self).__init__(*args, **kwargs)
        # parse the csv file to get the product ids

    def parse(self, response):
        with open(os.path.join(HERE, 'americanrv.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                p = Product()
                p['url'] = row['url']
                p['name'] = row['name']
                p['sku'] = row['sku']
                p['price'] = Decimal(row['price'] or 0)

                yield p

'''
    def parse(self, response):
        if not isinstance(response, HtmlResponse):
                    return
        hxs = HtmlXPathSelector(response)

        # pagination
        next_page = hxs.select(u'//a[contains(text(),"Next Page")]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0].replace('%%', '%25%25'))
            yield Request(next_page)

        # products
        products = hxs.select(u'//td[@width="120"]/a/@href').extract()
        for product in products:
            product = urljoin_rfc(get_base_url(response), product)
            yield Request(product, callback=self.parse_product)
    
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        res = {}
        hxs = HtmlXPathSelector(response)
        
        res['url'] = response.url
        name = hxs.select('//td[@class="page_headers"]/text()').extract()
        price = hxs.select('//td[@class="price-info"]//div[@id="price" and @class="price"]/text()').re(r'\$(.*)')
        model_no = hxs.select('//span[@id="product_id"]/text()').re(r'^.* ([a-zA-Z0-9\-\.]+)$')

        if name and price:
            csv_file = UnicodeReader(open(os.path.join(HERE, 'skus.csv')))
            for row in csv_file:
                if row[3] == model_no[0]:
                    res['sku'] = row[0]
                    name[0] = name[0]
                    break
            res['description'] = name[0]
            res['price'] = price
            yield load_product(res, response)
        else:
            return
'''
            
        
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
