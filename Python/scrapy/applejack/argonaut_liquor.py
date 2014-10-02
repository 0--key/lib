import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from urllib import urlencode
import hashlib

import csv

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.spiders.BeautifulSoup import BeautifulSoup
from scrapy import log

HERE = os.path.abspath(os.path.dirname(__file__))

class ArgonautLiquorSpider(BaseSpider):
    name = 'argonautliquor.com'
    allowed_domains = ['www.argonautliquor.com', 'argonautliquor.com']
    start_urls = ('http://www.argonautliquor.com', )

    def start_requests(self):
        url = 'http://www.argonautliquor.com/browsebrands?letter=%s'
        letters = ('(', '1', '3', '4', '6', '7', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
                   'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z')
        for letter in letters:
            yield Request(url % letter, callback=self.parse_brands, dont_filter=True)

        extra_categories = ('http://www.argonautliquor.com/results?brandid=21615',
                            'http://www.argonautliquor.com/results?brandid=21775',
                            'http://www.argonautliquor.com/results?brandid=14870')

        for url in extra_categories:
            yield Request(url, dont_filter=True)

    def parse_brands(self, response):
        soup = BeautifulSoup(response.body, convertEntities=BeautifulSoup.HTML_ENTITIES)
        brands = [ a['href'] for a in soup.find('td', id='main').findAll('a') if 'producers' in a['href'] ]
        for url in brands:
            url = urljoin_rfc(get_base_url(response), url)
            if '127.0.0.1' in url:
                url = url.replace('127.0.0.1', 'argonautliquor.com')
            yield Request(url, dont_filter=True)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        soup = BeautifulSoup(response.body, convertEntities=BeautifulSoup.HTML_ENTITIES)

        # categories
        # categories = hxs.select(u'//td[@id="left"]//a/@href').extract()
        # try:
            # categories = [a['href'] for a in soup.find('td', id='left').findAll('a')]
        # except AttributeError:
            # categories = []
        # for url in categories:
            # url = urljoin_rfc(get_base_url(response), url)
            # yield Request(url)

        # pagination
        next_page = hxs.select(u'//div[@class="pager"]/a[contains(text(),"Next")]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(get_base_url(response), next_page[0])
            if '127.0.0.1' in next_page:
                next_page = next_page.replace('127.0.0.1', 'argonautliquor.com')
            yield Request(next_page, dont_filter=True)
        else:
            next_page = soup.find(lambda tag: tag.name == 'a' and 'Next' in tag.text and tag.findParent('div', 'pager'))
            if next_page:
                next_page = urljoin_rfc(get_base_url(response), next_page['href'])
                if '127.0.0.1' in next_page:
                    next_page = next_page.replace('127.0.0.1', 'argonautliquor.com')
                yield Request(next_page, dont_filter=True)

        # products
        for product in self.parse_product(response):
            yield product
    
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        soup = BeautifulSoup(response.body, convertEntities=BeautifulSoup.HTML_ENTITIES)
        # products = hxs.select(u'//div[@class="itemResultsRow"]')
        try:
            products = soup.findAll('div', attrs={'class': 'itemResultsRow'})
        except AttributeError:
            products = []
        for product in products:
            # url = product.select(u'.//div[@class="itemTitle"]/a/@href').extract()[0]
            url = product.find('div', attrs={'class': 'itemTitle'}).find('a')['href']
            url = urljoin_rfc(get_base_url(response), url)
            # dropdown = product.select(u'.//select[@name="mv_order_item"]')
            dropdown = product.find('select', attrs={'name': 'mv_order_item'})
            if not dropdown:
                try:
                    # brand = product.select(u'.//div[@class="itemTitle"]/a/span[@class="brand"]/text()').extract()[0].strip()
                    brand = product.find('div', attrs={'class':'itemTitle'}).find('a').find('span', attrs={'class':'brand'}).text.strip()
                except AttributeError:
                    brand = u''
                # title = product.select(u'.//div[@class="itemTitle"]/a/span[@class="title"]/text()').extract()[0].strip()
                title = product.find('div', attrs={'class':'itemTitle'}).find('a').find('span', attrs={'class':'title'}).text.strip()
                try:
                    # vintage_age = product.select(u'.//div[@class="itemTitle"]/a/span[@class="vintageAge"]/text()').extract()[0].strip()
                    vintage_age = product.find('div', attrs={'class':'itemTitle'}).find('a').find('span', attrs={'class':'vintageAge'}).text.strip()
                except AttributeError:
                    vintage_age = u''
                # multiple_prices = product.select(u'.//td[@class="priceCell"]')
                multiple_prices = product.findAll('td', attrs={'class':'priceCell'})
                for option in multiple_prices:
                    name = u'%s %s %s' % (brand, title, vintage_age)
                    loader = ProductLoader(item=Product(), selector=option)
                    loader.add_value('url', url)
                    # price = option.select(u'.//p[@class="priceCellP salePriceP"]/span[@class="priceRetail"]/text()')
                    try:
                        price = option.find('p', attrs={'class': 'priceCellP salePriceP'}).find('span', attrs={'class': 'priceSale'}).text.strip()
                    except AttributeError:
                        price = option.find('p', attrs={'class': 'priceCellP'}).find('span', attrs={'class': 'priceRetail'}).text.strip()
                    # if not price:
                        # price = option.select(u'.//p[@class="priceCellP"]/span[@class="priceSale"]/text()')
                    # price = price[0].extract().strip()

                    # bottle_size = option.select(u'.//p[@class="priceCellP priceUnit"]/text()').extract()
                    bottle_size = option.find('p', attrs={'class': 'priceCellP priceUnit'})

                    if not bottle_size:
                        # bottle_size = option.select(u'.//p[@class="priceCellP"]/span[@class="priceUnit"]/text()').extract()
                        bottle_size = option.find(lambda tag: tag.name == 'span' and tag.get('class', '') == 'priceUnit' and tag.findParent('p', attrs={'class': 'priceCellP'}))
                    if bottle_size:
                        name += u' %s' % bottle_size.text.strip()
                    loader.add_value('name', name)
                    loader.add_value('price', price)
                    if loader.get_output_value('price'):
                        yield loader.load_item()
            else:
                # dropdown = dropdown[0]
                # brand = product.select(u'.//div[@class="itemTitle"]/a/span[@class="brand"]/text()').extract()[0].strip()
                # title = product.select(u'.//div[@class="itemTitle"]/a/span[@class="title"]/text()').extract()[0].strip()
                brand = product.find('div', attrs={'class':'itemTitle'}).find('a').find('span', attrs={'class':'brand'}).text.strip()
                title = product.find('div', attrs={'class':'itemTitle'}).find('a').find('span', attrs={'class':'title'}).text.strip()
                # for option in dropdown.select(u'./option/text()').extract():
                for option in [option.text for option in dropdown.findAll('option')]:
                    loader = ProductLoader(item=Product(), response=response)
                    loader.add_value('url', url)
                    name = u'%s %s' % (brand, title)
                    option = re.search(u'(.*?) \((.*)\)', option).groups()
                    name += u' %s' % option[1]
                    loader.add_value('name', name)
                    loader.add_value('price', option[0])
                    if loader.get_output_value('price'):
                        yield loader.load_item()
