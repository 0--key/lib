import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

import csv

from product_spiders.items import Product, ProductLoader
from product_spiders.spiders.BeautifulSoup import BeautifulSoup

class HGVDirectSpider(BaseSpider):
    name = 'hgvdirect.co.uk'
    allowed_domains = ['www.hgvdirect.co.uk']
    start_urls = ('http://www.hgvdirect.co.uk/catalog/allprods.php',)

    def __init__(self, *args, **kwargs):
        super(HGVDirectSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # pages
        next_page = hxs.select('//a[contains(text(), "Next")]/@href').extract()
        if next_page:
            url = urljoin_rfc(get_base_url(response), next_page[0])
            yield Request(url)
        else:
            soup = BeautifulSoup(response.body)
            next_page = soup.find('a', text=re.compile('.*Next.*'))
            if next_page:
                url = urljoin_rfc(get_base_url(response), next_page.parent['href'])
                yield Request(url)

        # products
        for product in self.parse_product(response):
            yield product


    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        # products
        products = hxs.select('//table[@class="productListing"]/tr')[1:]
        if len(products) < 20: # if the product list can not be parsed using lxml, use BeautifulSoup
            soup = BeautifulSoup(response.body)
            products = soup.find('table', {'class': 'productListing'}).findAll('tr')
            products = products[1:]
            for product in products:
                product_loader = ProductLoader(item=Product(), response=response)
                product = product.findAll('td')
                name = product[1].find('a').contents
                url = product[1].find('a')['href']
                price = product[2].text
                price = re.findall('[0-9\.]+', price)
                product_loader.add_value('name', name)
                product_loader.add_value('url', url)
                product_loader.add_value('price', price[0])
                yield product_loader.load_item()
                
        else:
            for product in products:
                product_loader = ProductLoader(item=Product(), selector=product)
                product_loader.add_xpath('name', './td[position()=2]/a/text()')
                product_loader.add_xpath('url', './td[position()=2]/a/@href')
                product_loader.add_xpath('price', './td[position()=3]', re='\xa3(.*[0-9])')
                yield product_loader.load_item()