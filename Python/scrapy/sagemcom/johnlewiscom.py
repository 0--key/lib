__author__ = 'juraseg'

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

import logging


class JohnlewisComSpider(BaseSpider):
    name = 'johnlewis.com'
    allowed_domains = ['johnlewis.com']
    start_urls = (
        'http://www.johnlewis.com/',
        )
    search_url = 'http://www.johnlewis.com/Search/Search.aspx?SearchTerm='

    keywords = ['Sagemcom']

    products = [
        'http://www.johnlewis.com/230898937/Product.aspx?SearchTerm=Humax+HDR-+FOX+500GB+T2',
        'http://www.johnlewis.com/231249320/Product.aspx?SearchTerm=Humax+HDR-+FOX+1TB+T2',
        'http://www.johnlewis.com/230913445/Product.aspx?SearchTerm=Humax+FOXSAT+500GB',
        'http://www.johnlewis.com/231395307/Product.aspx?SearchTerm=Panasonic+DMR+HW100+320GB',
        'http://www.johnlewis.com/231462460/Product.aspx',
        'http://www.johnlewis.com/230993658/Product.aspx',
        'http://www.johnlewis.com/230562595/Product.aspx',
        'http://www.johnlewis.com/231193482/Product.aspx?SearchTerm=sony+svr+hdt500',
        'http://www.johnlewis.com/231520735/Product.aspx',
        'http://www.johnlewis.com/231520734/Product.aspx',
        'http://www.johnlewis.com/231520732/Product.aspx',
        'http://www.johnlewis.com/231520733/Product.aspx',
        'http://www.johnlewis.com/231659104/Product.aspx',
        'http://www.johnlewis.com/231659103/Product.aspx',
        ]

    def start_requests(self):
        for keyword in self.keywords:
            url = self.search_url + keyword
            request = Request(url, callback=self.parse_search)
            yield request

        for url in self.products:
            yield Request(url, callback=self.parse_product)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)

        url = response.url

        name = hxs.select("//div[@id='divContentContainer']//div[@id='divProdHead']/h1/text()").extract()
        if not name:
            logging.error("ERROR! NO NAME! %s" % url)
            return
        name = name[0]

        price = hxs.select("//div[@id='divContentContainer']//div[@class='priceqty']/p[@class='price']/text()").extract()
        if not price:
            logging.error("ERROR! NO PRICE! %s %s" % (url, name))
            return
        price = price[0]

        l = ProductLoader(item=Product(), response=response)
        l.add_value('identifier', name)
        l.add_value('name', name)
        l.add_value('url', url)
        l.add_value('price', price)
        yield l.load_item()

    def parse_search(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        # parse pages
        pages = hxs.select("//div[@class='pagenum']/a/@href").extract()
        for page in pages:
            request = Request(urljoin_rfc(base_url, page), callback=self.parse_search)
            yield request

        # parse products
        items = hxs.select("//div[@class='grid-row']/div[@class='grid-item']")
        for item in items:
            name = item.select("div/a[@class='gridtitle']/text()").extract()
            if not name:
                continue
            name = name[0]

            url = item.select("div/a[@class='gridtitle']/@href").extract()
            if not url:
                logging.error("ERROR! NO URL! URL: %s. NAME: %s" % (response.url, name))
                continue
            url = url[0]
            url = urljoin_rfc(base_url, url)

            price = item.select("div/a[@class='price']/text()").extract()
            if not price:
                logging.error("ERROR! NO PRICE! URL: %s. NAME: %s" % (response.url, name))
                continue
            price = price[0]

            l = ProductLoader(item=Product(), response=response)
            l.add_value('identifier', name)
            l.add_value('name', name)
            l.add_value('url', url)
            l.add_value('price', price)
            yield l.load_item()
