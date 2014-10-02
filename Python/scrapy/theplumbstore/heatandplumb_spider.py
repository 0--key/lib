import csv
import os
import copy
import shutil

from scrapy import log
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.http.cookies import CookieJar

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class HeatAndPlumbSpider(BaseSpider):
    name = 'heatandplumb.com'
    allowed_domains = ['heatandplumb.com']
    start_urls = ['http://www.heatandplumb.com']

    def __init__(self, *args, **kwargs):
        super(HeatAndPlumbSpider, self).__init__(*args, **kwargs)
        csv_file = csv.reader(open(os.path.join(HERE, 'theplumbstore_list.csv')))
        self.mpns = [row[5] for row in csv_file if row[7].lower()=='yes' ]

    def start_requests(self):
        for mpn in self.mpns:
            if mpn:
                url = 'http://www.heatandplumb.com/search.php?q=%s&search=Search' % mpn
                yield Request(url, meta={'mpn':mpn})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//td[@onclick and descendant::table'
                              '[@width="100%" and @cellspacing="2"'
                              ' and @cellpadding="2" and @border="0"]'
                              '/tr[descendant::td[@valign="top"]/b/text()]]')
        try:
            product = products[0]
            url = product.select('@onclick').extract()[0].split("='")[-1].replace("';",'')
            name = ''.join(product.select('table/tr/td/b/text()').extract())
            yield Request(urljoin_rfc(get_base_url(response), url), 
                          callback=self.parse_product, 
                          meta={'mpn':response.meta['mpn'], 'name':name})
        except IndexError:
            log.msg('No results for MPN:%s ' % response.meta['mpn'])

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        loader = ProductLoader(item=Product(), response=response)
        #loader.add_value('sku', response.meta['mpn'])
        mpn = hxs.select('//div[@class="prod_info_container"]/h1/i/text()').extract()
        if not mpn:
            mpn = hxs.select('//li/span[@itemprop="identifier"]/text()').extract()
        name = ' '.join((response.meta['name'], mpn[0]))
        loader.add_value('identifier', mpn[0])
        loader.add_value('name', name)
        loader.add_value('url', response.url)
        loader.add_xpath('price', '//td[@class="radioPadding" and @width="90" and @bgcolor="#f2f2f2" and @align="center"]/text()')
        yield loader.load_item()
        
