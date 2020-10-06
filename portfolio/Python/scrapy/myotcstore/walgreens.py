import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode
from scrapy import log

import csv

from product_spiders.items import Product, ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))
CSV_FILENAME = os.path.join(os.path.dirname(__file__), 'walgreens.csv')

def normalize_name(name):
    name = re.sub(' +', ' ', name).strip().lower()
    name = name.replace('\n', '')
    return name

class WalgreensSpider(BaseSpider):
    name = 'walgreens.com'
    allowed_domains = ['www.walgreens.com', 'walgreens.com']
    start_urls = ('http://walgreens.com/site_map.jsp',)
    #start_urls = ('http://www.walgreens.com/store/c/face-moisturizers/ID=360495-tier3', )

    def __init__(self, *args, **kwargs):
        super(WalgreensSpider, self).__init__(*args, **kwargs)
        self.names = {}
        with open(CSV_FILENAME) as f:
           reader = csv.DictReader(f)
           for row in reader:
               prod_id = re.search('ID=prod(\d+)', row['url']).groups()[0]
               self.names[prod_id] = row['name'].decode('utf-8', 'ignore')

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # brands
        brands = hxs.select(u'//div[@id="shop_content"]//li[not(@class="first")]//a/@href').extract()
        for url in brands:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url)

        cats = hxs.select('//h2[text()="Product Category"]/following-sibling::div[1]/form[@id="product-refinement"]//a/@href').extract()
        for url in cats:
            yield Request(urljoin_rfc(get_base_url(response), url))

        #show_all = hxs.select(u'//div[@class="sidenav-content gray top-level"]//a[contains(text(),"Shop All")]/@href').extract()
        show_all = hxs.select('//p[@class="arrow_sym"]/a[@class="SearchLinkBold" and starts-with(@title, "View More")]/@href').extract()
        if show_all:
            for url in show_all:
                link = urljoin_rfc(get_base_url(response), url)
                yield Request(link)


        next_page = hxs.select(u'//div[@id="pagination" and @class="pagination"]//a[child::img and @title="Next Page"]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(next_page)

        # products
        for product in self.parse_product(response):
            yield product


    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)
        products = hxs.select(u'//div[contains(@class,"product-container")]')

        for product in products:
            product_loader = ProductLoader(item=Product(), selector=product)
            url = product.select(u'.//a[@class="SearchLinkBold"]/@href').extract()[0]
            url = urljoin_rfc(get_base_url(response), url)
            product_loader.add_value('url', url)
            name = product.select(u'.//a[@class="SearchLinkBold"]/text()').extract()[0]

            extra_name = product.select(u'.//div[contains(@class,"prod-info-box")]/p/text()').extract()
            if extra_name:
                name += ' ' + extra_name[0]

            r = re.search('ID=prod(\d+)', url)
            if r:
                log.msg('Found ' + r.groups()[0])
                name = self.names.get(r.groups()[0], name)
            product_loader.add_value('name', name)
            #product_loader.add_xpath('price', u'.//div[@class="pricing"]/div[@class="prod-pricing"]/p[not(@class="strike_thru")]/b[@class="price sale"]/text()',
            #                                 re=u'.*?or 1/\$(.*)')
            #product_loader.add_xpath('price', u'.//div[@class="pricing"]/div[@class="prod-pricing"]/p[not(@class="strike_thru")]/b[@class="price sale"]/text()',
            #                                 re=u'\$(.*)')
            #product_loader.add_xpath('price', u'.//div[@class="pricing"]/div[@class="prod-pricing"]/p[not(@class="strike_thru")]/b/text()',
            #                                 re=u'.*?or 1/\$(.*)')
            #product_loader.add_xpath('price', u'.//div[@class="pricing"]/div[@class="prod-pricing"]/p[not(@class="strike_thru")]/b/text()',
            #                     re=u'\$(.*)')
            product_loader.add_xpath('price', './/p[@class="FSprice"]/text()', re=u'.*?or 1/\$(.*)')
            product_loader.add_xpath('price', './/p[@class="FSprice"]/text()', re=u'.*?or 1/\$(.*)')
            product_loader.add_xpath('price', './/p[@class="Rprice"]/text()')
            product_loader.add_xpath('price', './/p[@class="Rprice"]/text()')
            if not product_loader.get_output_value('price'):
                continue
            yield product_loader.load_item()
