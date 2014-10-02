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

class tweetysDOSpider(BaseSpider):
    name = 'tweetys.com_DO'
    allowed_domains = ['www.tweetys.com','tweetys.com']
    start_urls = ('http://www.tweetys.com/search.aspx?find=',)

    def __init__(self, *args, **kwargs):
        super(tweetysDOSpider, self).__init__(*args, **kwargs)
        self.URLBASE = 'http://tweetys.com/'

        # parse the csv file to get the product ids
        self.csv_file = UnicodeReader(open(os.path.join(HERE, 'skus.csv')))

    def start_requests(self):
        for row in self.csv_file:
            url = self.URLBASE + 'search.aspx?find=' + row[1]
            request = Request(url,callback=self.parse_search)
            request.meta['sku'] = row[0]
            request.meta['search_q'] = row[1]
            yield request
        yield Request('http://tweetys.com/search.aspx?find=',callback=self.parse)
            
    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        product_urls = hxs.select('//div[@class="product-list-item"]/a/@href').extract()
        for product in product_urls:
            request = Request(urljoin_rfc(base_url,product), callback=self.parse_product)
            yield request
            
        pages = hxs.select('//a[@title="Go to the next page"]/@href').extract()
        for page in pages:
            request = Request(urljoin_rfc(base_url,page), callback=self.parse)
            yield request
            

    def parse_search(self, response):
        if not isinstance(response, HtmlResponse):
            return
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        
        product_urls = hxs.select('//div[@class="product-list-item"]/a/@href').extract()
        if product_urls:
            request = Request(urljoin_rfc(base_url,product_urls[0]+'?search_q='+response.meta['search_q']), callback=self.parse_product)
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
        options = hxs.select("//select[contains(@name,'ddlVariationGroup')]/option")
        res = {}
        if not options:
            #no options
            name = hxs.select("//div[@id='product-detail-div']/h1/text()")[0].extract().strip()
            url = response.url
            price = "".join(hxs.select('//span[@class="prod-detail-cost-value"]/text()').re(r'([0-9\,\. ]+)')).strip()
            res['url'] = url
            res['description'] = name
            res['price'] = price
            if 'sku' in response.meta:
                res['sku'] = response.meta['sku']
            yield load_product(res, response)
        else:
            is_multioptions = hxs.select("//select[contains(@name,'ddlVariationGroup')]")
            if len(is_multioptions) < 2:
                for option in options:
                    select_name = hxs.select("//select[contains(@name,'ddlVariationGroup')]/@name").extract()[0]
                    request = FormRequest.from_response(response, formdata={select_name: option.select('./@value').extract()},
                                                    dont_click=True, callback=self.parse_options)
                    request.meta['name2'] = option.select('./text()').extract()[0].strip()
                    if 'sku' in response.meta:
                        request.meta['sku'] = response.meta['sku']
                    if 'search_q' in response.meta:
                        request.meta['search_q'] = response.meta['search_q']
                    yield request
                
    def parse_options(self, response):
        if not isinstance(response, HtmlResponse):
            return
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        res = {}
        if 'search_q' in response.meta:
            sku_ = hxs.select("//span[@class='prod-detail-part-value']/text()[contains(.,'"+ response.meta['search_q'] +"')]").extract()
            #log.msg('SEARCH_Q: '+ response.meta['search_q'])
            if sku_:
                name = hxs.select("//div[@id='product-detail-div']/h1/text()")[0].extract().strip()
                url = response.url
                price = "".join(hxs.select('//span[@class="prod-detail-cost-value"]/text()').re(r'([0-9\,\. ]+)')).strip()
                res['url'] = url
                res['description'] = name + ' ' + response.meta['name2']
                res['price'] = price
                res['sku'] = response.meta['sku']
                yield load_product(res, response)
        else:
            name = hxs.select("//div[@id='product-detail-div']/h1/text()")[0].extract().strip()
            url = response.url
            price = "".join(hxs.select('//span[@class="prod-detail-cost-value"]/text()').re(r'([0-9\,\. ]+)')).strip()
            res['url'] = url
            res['description'] = name + ' ' + response.meta['name2']
            res['price'] = price
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
