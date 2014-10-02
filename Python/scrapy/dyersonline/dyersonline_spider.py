import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy import log
from scrapy.http import FormRequest
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals

from productloader import load_product
import csv, codecs, cStringIO

Current_dir = os.path.abspath(os.path.dirname(__file__))

class dyersonline_spider(BaseSpider):
    name = 'dyersonline.com'
    allowed_domains = ['dyersonline.com', 'www.dyersonline.com']              
    start_urls = ('http://www.dyersonline.com',)    
    

    @classmethod
    def spider_opened(spider):
        if spider.name == 'dyersonline.com':
            log.msg("opened spider %s" % spider.name)      

    @classmethod
    def spider_closed(spider):
        if spider.name == 'dyersonline.com':
            if os.path.exists(os.path.join(Current_dir,'skus_.csv')):
                try:
                    os.remove(os.path.join(Current_dir,'skus.csv'))
                except:
                    print log.msg("No sku.csv file!")
                os.rename(os.path.join(Current_dir,'skus_.csv'),os.path.join(Current_dir,'skus.csv'))

    def __init__(self, *args, **kwargs):
        super(dyersonline_spider, self).__init__(*args, **kwargs)
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)        

        # parse the csv file to get the product ids
        self.csv_writer = UnicodeWriter(open(os.path.join(Current_dir,'skus_.csv'), 'wb'),dialect='excel')

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        base_url = get_base_url(response)
        
        #categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//div[@class="nav-container"]/ul[@id="nav"]/li/ul/li/a/@href').extract()
        for url in category_urls:
            yield Request(url)
            
        #pages
        page_urls = hxs.select('//div[@class="pages"]/ol/li/a/@href').extract()
        for page in page_urls:
          yield Request(page)
          
        acategory_urls = hxs.select('//div[@class="category-image"]/a/@href').extract()
        for aurl in acategory_urls:
          yield Request(aurl)

            
        #products
        products = hxs.select('//div[@class="category-products"]/ul/li/a/@href').extract()
        for p in products:
            yield Request(p, callback=self.parse_product)
            
    def parse_product(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        res = {}
        
        name = hxs.select("//div[@class='product-name']/h1/text()").extract()
        url = response.url
        price = "".join(hxs.select("//div[@class='col-right']/div/div[@class='price-block']/span/span[@class='price']/text()").re(r'([0-9\,\. ]+)')).strip()
        if not price:
            price = "".join(hxs.select("//div[@class='col-right']/div/p[@class='special-price']/span[@class='price']/text()").re(r'([0-9\,\. ]+)')).strip()
        sku =  hxs.select("//dd[@class='identifier']/text()")[0].extract()
        res['url'] = urljoin_rfc(base_url,url)
        res['description'] = sku + ' ' + name[0].strip()
        res['price'] = price
        res['sku'] = sku
        sku2 = hxs.select("//div[@class='1']/text()").extract()
        if not sku2:
            sku2_ = 0
        else:
            sku2_ = sku2[0]
        sku3 = hxs.select("//div[@class='2']/text()").extract()            
        if not sku3:
            sku3_ = 0
        else:
            sku3_ = sku3[0]
        model = hxs.select("//dd[@class='model']/text()").extract()    
        if not model:
            model_ = ''
        else:
            model_ = model[0]
        self.csv_writer.writerow([res['sku'],sku2_,sku3_,model_,name[0].strip()])
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
        self.writer.writerow([str(s).encode("utf-8") for s in row])
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
