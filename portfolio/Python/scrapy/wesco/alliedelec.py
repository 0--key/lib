import csv
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader


HERE = os.path.abspath(os.path.dirname(__file__))

class AllieDelecSpider(BaseSpider):
    name = 'alliedelec.com'
    allowed_domains = ['alliedelec.com']

    def start_requests(self):
        with open(os.path.join(HERE, 'products.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                sku = row['Part #']

                url = 'http://www.alliedelec.com/search/searchresults.aspx?dsNav=Ntk:MfrPartNumber\
|%(sku)s|3|,Ny:False,Ro:0&SearchType=2&fromsearch=true&term=%(sku)s' % {'sku': sku}

                yield Request(url, meta={'sku': sku})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        product = hxs.select('//table[@id="tblParts"]//tr[@onmouseout]')

        if product:
            loader = ProductLoader(item=Product(), selector=product[0])
            loader.add_xpath('name', './td[3]/div/a//text()')
            url = product.select('./td[3]/div/a/@href').extract()[0]
            url = urljoin_rfc(get_base_url(response), url)
            loader.add_value('url', url)
            loader.add_xpath('price', './td[6]//text()', re='\$(.*)')
            loader.add_xpath('sku', './td[3]/div/a[2]/text()')
            if loader.get_output_value('sku') == response.meta['sku'].lower():
                yield loader.load_item()
