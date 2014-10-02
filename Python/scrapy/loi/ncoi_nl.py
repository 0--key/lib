import re
import logging

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class NcoiNlSpider(BaseSpider):
    name = 'ncoi.nl'
    allowed_domains = ['ncoi.nl']
    start_urls = ('http://www.ncoi.nl',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//div[@id="sub"]/ul/li/a/@href').extract():
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse2)

    def parse2(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//div[@id="sub"]/ul/li/div/ul/li/a[not(contains(text(),"Alle"))]/@href').extract():
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_course_list)

    def parse_course_list(self, response):
        hxs = HtmlXPathSelector(response)

        url_list = hxs.select(u'//div[@class="courselist"]//h3/a/@href').extract()
        path = hxs.select(u'//ul[@id="breadcrumbs"]/li/a/text()').extract()
        path.extend(hxs.select(u'//ul[@id="breadcrumbs"]/li[last()]/text()').extract())
        path.pop(0)
        for url in url_list:
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
        price1 = costs.select(u'.//tr/td[contains(text(),"Cursusgeld")]/../td[position()=2]/text()').extract()
        price2 = costs.select(u'.//tr/td[contains(text(),"Studiemateriaal")]/../td[position()=2]/text()').extract()

        pricetxt = costs.select(u'./p/text()').extract()
        # Just because one course has price in DIVs not single P
        pricetxt.extend(costs.select(u'./div/text()').extract())

        if not price1 or not price2:
            for line in pricetxt:
                if 'Cursusgeld' in line:
                    price1 = [line.split(':')[1].split('(')[0]]

                # Just because one course specifies price with multiple P tags
                elif 'Module C1 en C2' in line:
                    price1 = [re.search(u'([\d.,]+)', line.split(u'\u20ac')[1]).group(1)]
                elif 'Inschrijfgeld' in line:
                    price1 = [line.split(':')[1].split('(')[0]]
                elif 'Trainingskosten' in line:
                    price1 = [line.split(':')[1].split('(')[0]]
                elif 'Studiemateriaal' in line:
                    price2 = [line.split(':')[1].split('(')[0]]
                elif 'Trainingsmateriaal' in line:
                    price2 = [line.split(':')[1].split('(')[0]]

            if not price1:
                for line in pricetxt:
                    line = line.strip()
                    if line.startswith(u'\u20ac'):
                        price1 = [re.search(u'([\d.,]+)', line.split(u'\u20ac')[1]).group(1)]
                    elif line.startswith('20') and line[4] == ':':
                        price1 = [line.split(':')[1]]
                    elif line.startswith('Opleiding'):
                        price1 = [re.search(u'([\d.,]+)', line.split(u'\u20ac')[1]).group(1)]

        try:
            # This seems to be optional
            if not price2:
                price2 = ['0']
            price = float(price1[0].replace(u'\u20ac', '').replace('-', '').replace('.', '').replace(',', '.')) \
                    + float(price2[0].replace(u'\u20ac', '').replace('-', '').replace('.', '').replace(',', '.'))
        except Exception, e:
            logging.error('Bad price [%s] (%s)' % (pricetxt, e))
            
        product_loader.add_value('price', price)
        yield product_loader.load_item()
