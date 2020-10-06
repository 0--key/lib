import re
import logging

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class ScheideggerNlSpider(BaseSpider):
    name = 'scheidegger.nl'
    allowed_domains = ['scheidegger.nl']
    start_urls = ('http://www.scheidegger.nl',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//div[@id="sub"]/ul/li/a/@href').extract():
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_course_list)

    def parse_course_list(self, response):
        hxs = HtmlXPathSelector(response)

        path = hxs.select(u'//ul[@id="breadcrumbs"]/li/a/text()').extract()
        path.extend(hxs.select(u'//ul[@id="breadcrumbs"]/li[last()]/text()').extract())
        path.pop(0)
        for url in hxs.select(u'//h2[@class="coursetitle"]/a/@href').extract():
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, meta={'path':path}, callback=self.parse_course)

    def parse_course(self, response):
        hxs = HtmlXPathSelector(response)

        path = response.meta['path'][:]
        path.extend(hxs.select(u'//h1/text()').extract())

        product_loader = ProductLoader(item=Product(), selector=hxs)
        product_loader.add_value('name', u' / '.join((p.strip() for p in path)))
        product_loader.add_value('url', response.url)
 
        costs = hxs.select(u'//div[@id="kostenspecificatie"]')
        pricetxt = costs.select(u'./p[1]/text()').extract()
        if len(pricetxt) == 1:
            pricetxt = costs.select(u'./p[2]/text()').extract()
        try:
            for line in pricetxt:
                if 'Lesgeld' in line or 'Cursusgeld' in line:
                    groups = re.search(u'([\d.,]+).*\( *([\d.,]+) lessen\)', line)
                    if groups:
                        price = float(groups.group(2)) * float(groups.group(1).replace('.', '').replace(',', '.'))
                        break
                    groups = re.search(u'([\d.,]+).*\(.*\)', line)
                    if groups:
                        price = float(groups.group(1).replace('.', '').replace(',', '.'))
                        break
                elif 'Trainingskosten' in line:
                    price = line.split(':')[1].replace(u'\u20ac', '').replace('-', '')
                    price = float(price.replace('.', '').replace(',', '.'))
                    break
                    
            product_loader.add_value('price', price)
        except Exception, e:
            logging.error("Bad price [%s] found at URL [%s] (%s)" % (pricetxt, response.url, e))

        yield product_loader.load_item()
