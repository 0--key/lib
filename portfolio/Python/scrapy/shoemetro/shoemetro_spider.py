import csv
import os
import copy
import re
import shutil
import hashlib

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.http.cookies import CookieJar
from scrapy import log
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from product_spiders.spiders.BeautifulSoup import BeautifulSoup

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))

class ShoeMetroSpider(BaseSpider):
    name = 'shoemetro.com'
    allowed_domains = ['shoemetro.com']
    start_urls = ('http://www.shoemetro.com/nsearch.aspx?shown=96&sort_by_field=Price:ASC&display_type=List',)

    def __init__(self, *a, **kw):
        super(ShoeMetroSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        if spider.name == self.name:
            shutil.copy('data/%s_products.csv' % spider.crawl_id, os.path.join(HERE, 'shoemetroall.csv'))
            log.msg("CSV is copied")

    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        p = re.compile('of <b>(\d+)</b', re.IGNORECASE)
        total = p.findall(hxs.extract())
        pages = int(int(total[0])/96) + 2
        for i in range(1, pages):
            next_url = self.start_urls[0] + "&page=" + str(i)
            yield Request(next_url, meta={'cur': i, 'attempt': 1}, callback=self.parse_items)

    def parse_items(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        cur_page = hxs.select('//span[@class="currentPage"]/text()').extract()
        if cur_page and (int(cur_page[0]) != response.meta['cur']) and (response.meta['attempt'] < 5):
            log.msg('WRONG PAGE! ONE MORE ATTEMPT to ' + response.url)
            yield Request(response.url + '&at=' + str(response.meta['attempt']), meta={'cur': response.meta['cur'], 'attempt': response.meta['attempt'] + 1}, dont_filter=True, callback=self.parse_items)
            return
        soup = BeautifulSoup(response.body)
        products = [a['href'] for a in soup.findAll(lambda tag: tag.name=='a' and tag.findChild('b') and tag.findParent('td', {'colspan': 2}))]
        for url in products:
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product)
        """trs = hxs.select('//div[@id="mainContent"]//table[@style="height:100%"]/tr')
        tr = 0
        while (tr < len(trs)):
            sku = ""
            url = trs[tr+1].select('.//a/@href').extract()
            if url:
                url = url[0]
            else:
                url = ""
            price = trs[tr+1].select('.//span[@class="variantprice"]/text()').extract()
            if price:
                price = price[0]
            else:
                price = ''
                log.msg('NO PRICE: ' + str(response.meta['attempt']))
            tds=trs[tr+2].select('.//td[@valign="top"]/text()').extract()
            if tds:
                tds = tds[0]
            else:
                tds = " "
            name = ''
            nm = re.search('& Style - (.*)Width', tds)
            if nm: 
                name = nm.group(1).strip()

            color = trs[tr+2].select("td[@valign='top']/text()").re("True Color - (.*?)Upper")
            if color: 
                name = name + ' ' + color[0].strip()
            if name and price:
                #sku = hashlib.md5()
                #sku.update(name)
                #loader = ProductLoader(item=Product(), response=response)
                #loader.add_value('url', urljoin_rfc(base_url,url))
                #loader.add_value('name', name)
                #loader.add_value('sku', sku.hexdigest())
                #loader.add_value('price', price)
                #loader.add_value('identifier', sku.hexdigest())
                yield Request(urljoin_rfc(base_url,url), callback=self.parse_product, meta={'name':name})#loader.load_item()
            tr += 4"""

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        # name = response.meta['name']
        product_data = ' '.join(hxs.select(u'//div[@id="productDescription"]//text()').extract()).strip()
        name_regexp = re.compile(u'.*Style +?- (.*?)Width')
        color_regexp = re.compile(u'.*True Color +?- (.*?)Upper')
        name = name_regexp.search(product_data).group(1).strip()
        color = color_regexp.search(product_data).group(1).strip()
        name += u' %s' % color
        options = hxs.select('//*[@id="productOptionsWrap"]/select/option[@sku]')
        if options:
            for option in options:
                loader = ProductLoader(item=Product(), selector=hxs)
                loader.add_value('url', response.url)
                size = option.select('text()').extract()[0]
                loader.add_value('name', ' '.join((name,size)))
                sku = option.select('@sku').extract()[0]
                loader.add_value('sku', sku)
                value_option = option.select('@value').extract()[0]
                price = hxs.select('//*[@id="variantPrice%s"]/span[@class="price"]/text()' % value_option).extract()
                loader.add_value('price', price)
                loader.add_value('identifier', sku)
                yield loader.load_item()
        #else:
        #    loader = ProductLoader(item=Product(), response=response)
        #    loader.add_value('url', response.url)
        #    size = ''.join(hxs.select('//*[@id="cartBoxWrap"]/div/div[@class="oneVariantName"]/text()').extract())
        #    loader.add_value('name', ' '.join((name,size)))
        #    loader.add_xpath('price', '//*[@id="productPriceWrap"]/div[@class="varPrice"]/span[@class="price"]/text()')
        #    yield loader.load_item()
            
"""
    def start_requests(self):
        with open(os.path.join(HERE, 'shoemetro.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                sku = row['sku']
                yield Request(row['url'], meta={'sku': sku, 'name': row['name']}, callback=self.parse_product)

    def parse_product(self, response):
        if 'productnotfound' in response.url:
            return

        hxs = HtmlXPathSelector(response)

        name = hxs.select('//h1[@id="ProductNameText"]/text()').extract()[0]
        opt = hxs.select('//option[@sku="%s"]' % response.meta['sku'])
        if not opt:
            loader = ProductLoader(item=Product(), response=response)
            loader.add_value('url', response.url)
            loader.add_value('name', response.meta['name'])
            loader.add_value('sku', response.meta['sku'])
            loader.add_xpath('price', '//div[contains(@id, "variantPrice")]//span[@class="price"]/text()')
            yield loader.load_item()
            return

        opt = opt[0]
        name += ' ' + opt.select('./text()').extract()[0]
        prod_id = opt.select('./@value').extract()[0]
        loader = ProductLoader(item=Product(), response=response)
        loader.add_value('url', response.url)
        loader.add_value('name', response.meta['name'])
        loader.add_value('sku', response.meta['sku'])
        loader.add_xpath('price', '//div[@id="variantPrice%s"]//span[@class="price"]/text()' % prod_id)

        yield loader.load_item()

################## Older code ========================

class ShoeMetroSpider(BaseSpider):
    name = 'shoemetro.com'
    allowed_domains = ['shoemetro.com']

    def start_requests(self):
        with open(os.path.join(HERE, 'products.csv')) as f:
            reader = csv.DictReader(f)
            for row in reader:
                sku = row['sku']

                name = row['brand style'].lower()
                url = 'http://www.shoemetro.com/nsearch.aspx?keywords=%s&shown=96'
                brand = row['brand']
                style = row['style']
                query = (brand + ' ' + style).replace(' ', '+')

                yield Request(url % sku, meta={'sku': sku, 'name': name})
                yield Request(url % query, meta={'sku': sku, 'name': name})

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        products = hxs.select('//div[@id="mainContent"]//a[starts-with(@href, "/p-")]/@href').extract()
        for product in products:
            url_name = ' '.join(product.split('-')[2:]).replace('.aspx', '').replace('.', '')
            if response.meta['name'] in url_name:
                yield Request(urljoin_rfc(get_base_url(response), product), callback=self.parse_product,
                              meta={'sku': response.meta['sku']})

    def parse_product(self, response):
        if 'productnotfound' in response.url:
            return

        hxs = HtmlXPathSelector(response)

        name = hxs.select('//h1[@id="ProductNameText"]/text()').extract()[0]
        opt = hxs.select('//option[@sku="%s"]' % response.meta['sku'])
        if not opt:
            loader = ProductLoader(item=Product(), response=response)
            loader.add_value('url', response.url)
            loader.add_value('name', name)
            loader.add_value('sku', response.meta['sku'])
            loader.add_xpath('price', '//div[contains(@id, "variantPrice")]//span[@class="price"]/text()')
            yield loader.load_item()
            return

        opt = opt[0]
        name += ' ' + opt.select('./text()').extract()[0]
        prod_id = opt.select('./@value').extract()[0]
        loader = ProductLoader(item=Product(), response=response)
        loader.add_value('url', response.url)
        loader.add_value('name', name)
        loader.add_value('sku', response.meta['sku'])
        loader.add_xpath('price', '//div[@id="variantPrice%s"]//span[@class="price"]/text()' % prod_id)

        yield loader.load_item()

"""
