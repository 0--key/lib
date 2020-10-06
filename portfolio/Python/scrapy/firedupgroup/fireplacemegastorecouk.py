import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader


class FireplacemegastoreCoUkSpider(BaseSpider):
    name = 'fireplacemegastore.co.uk'
    allowed_domains = ['fireplacemegastore.co.uk']
    start_urls = ('http://fireplacemegastore.co.uk/',)

    def parse(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select("//td[@class='bkleft']/table/tr/td/table/tr/td/a/@href").extract()
        for url in category_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        # pages
        page_urls = hxs.select("//a[@class='page-off']/@href").extract()
        for url in page_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        # products list
        products = hxs.select("//div[@id='content']/table[4]/tr/td[4]/table/tr[2]/td/table[2]/tr")
        if not products:
            print "ERROR!! NO PRODUCTS!! %s " % response.url
        for product_el in products:
            if len(product_el.select("td")) < 5:
                continue
            name = product_el.select("td[2]/span[@class='txttitred']/a/text()").extract()
            if not name:
                print "ERROR!! NO NAME!! %s" % response.url
                continue

            url = product_el.select("td[2]/span[@class='txttitred']/a/@href").extract()
            if not url:
                print "ERROR!! NO URL!! %s" % response.url
                continue
            url = url[0]
            url = urljoin_rfc(URL_BASE, url)

            price = product_el.select("td[4]/span[@class='txtnr']/text()").extract()
            if not price:
                print "ERROR!! NO PRICE!! %s" % response.url
                continue
            price = price[0]
            # check for negative price (yes, it's a weird but this site has negative prices)
            m = re.search('(-)?\xa3([\d\.,]+)', price, re.UNICODE)
            if m.group(1) == "-":
                # take usual price
                price = product_el.select("td[4]/s/text()").extract()
                if not price:
                    print "ERROR!! NO PRICE!! Product %s, url %s" % (name, response.url)
                    continue
                price = price[0]
            else:
                price = m.group(2)

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)
            loader.add_value('sku', '')
            yield loader.load_item()
