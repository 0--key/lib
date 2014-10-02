import re
import logging

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

def parse_price(price_str):
    c_index = price_str.rfind(',')
    d_index = price_str.rfind('.')
    if c_index > -1 and d_index > -1:
        if c_index > d_index:
            return float(price_str.replace('.', '').replace(',', '.'))
        elif d_index > c_index:
            return float(price_str.replace(',', ''))
    elif c_index > -1:
        if len(price_str.split(',')[-1]) == 3:
            return float(price_str.replace(',', ''))
        else:
            return float(price_str.replace(',', '.'))
    elif d_index > -1:
        if len(price_str.split('.')[-1]) == 3:
            return float(price_str.replace('.', ''))
        else:
            return float(price_str)
    else:
        return float(price_str)
 
class LoiNlSpider(BaseSpider):
    name = 'loi.nl'
    allowed_domains = ['loi.nl']
    start_urls = ('http://www.loi.nl',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//ul[@class="mainnav"]/li/a/@href').extract():
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse2)

    def parse2(self, response):
        hxs = HtmlXPathSelector(response)

        # Some pages have list inside iframe
        iframe = hxs.select(u'//div[@id="main_content"]//iframe/@src').extract()
        if iframe:
            yield Request(iframe[0], callback=self.parse2)
            return
            
        cats = hxs.select(u'//div[starts-with(@class,"vakgebied_niveau")]//li/a/@href').extract()
        cats.extend(hxs.select(u'//ul[@class="aoi_lijstje"]//li/a/@href').extract())
        if cats:
            for url in cats:
                url = urljoin_rfc(get_base_url(response), url)
                yield Request(url, callback=self.parse2)
        else:
            price = hxs.select(u'//div[@id="ihk"]//td/label[text()="Nu tijdelijk"]/../../td[last()]/p/text()').extract()
            if not price:
                price = hxs.select(u'//div[@id="ihk"]//td/label[text()="Collegegeld" or text()="Lesgeld"]/../../td[last()]/text()').extract()

            if not price:
                logging.error("No price found at URL [%s]" % (response.url))
                return

            price_orig = price[0]
            price = price[0].replace(' ', '').replace(u'\u20ac', '')
            groups = re.search(u'(\d+)x([\d.,]+)', price)
            if not groups:
                logging.error("Bad price [%s] found at URL [%s]" % (price_orig, response.url))
                return

            price = float(groups.group(1)) * parse_price(groups.group(2))

            path = hxs.select(u'//ul[@id="pathul"]/li/a/@title').extract()
            # remove Home
            path.pop(0)

            # Course name is without URL
            # XXX this is category name for some
            course_name = hxs.select(u'//ul[@id="pathul"]/li[last()]/text()').extract()[0]
            path.append(course_name.replace('>', ''))

            title = ' '.join(hxs.select(u'//h1/text()').extract()).strip()
            if title not in path:
                path.append(title)

            product_loader = ProductLoader(item=Product(), selector=hxs)
            product_loader.add_value('name', u' / '.join((p.strip() for p in path)))
            product_loader.add_value('url', response.url)
            product_loader.add_value('price', price)
            yield product_loader.load_item()
