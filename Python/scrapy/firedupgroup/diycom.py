import logging

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

class DiyComSpider(BaseSpider):
    name = 'diy.com'
    allowed_domains = ['diy.com']
    start_urls = ('http://www.diy.com/nav/rooms/fires-surrounds',)

    pager_url_arguments = "?fh_view_size=150&fh_start_index=0"

    def parse(self, response):
        URL_BASE = get_base_url(response)
        #categories
        hxs = HtmlXPathSelector(response)
        categories_title = hxs.select('//div[@id="secondNav"]/div[@class="catList"]/dl/dt[1]/text()').extract()
        if categories_title and categories_title[0].strip().lower() == "by category":
            categories = hxs.select('//div[@id="secondNav"]/div[@class="catList"]/dl/dd')
            for link in categories:
                url = link.select(".//a/@href").extract()[0]
                url = urljoin_rfc(URL_BASE, url)
                url += self.pager_url_arguments
                yield Request(url)
                link_class = link.select("@class").extract()
                if link_class and link_class[0] == "last":
                    break

        pages_urls = hxs.select('//span[@clas="pagingTools"]/a/@href').extract()
        for url in pages_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        products_els = hxs.select('//li[@class="galleryProduct"]')
        for product_el in products_els:
            name = product_el.select('div[@class="galleryContainer"]/a/span/text()').extract()
            if not name:
                print "ERROR!! NO NAME!! %s" % response.url
                continue
            name = name[0].split(" - Home Delivered")

            url = product_el.select('div[@class="galleryContainer"]/a/@href').extract()
            if not url:
                print "ERROR!! NO URL!! %s" % response.url
                continue
            url = url[0]
            url = urljoin_rfc(URL_BASE, url)

            price = product_el.select(
                'div[@class="galleryContainer"]/div[@class="productInfo"]/\
                 div[@class="productPriceBlock"]/p/span[@class="nowPrice"]/strong/text() |\
                 div[@class="galleryContainer"]/div[@class="productInfo"]/\
                 div[@class="productPriceBlock"]/p/span[@class="onlyPrice"]/text()'
            ).extract()
            if not price:
                print "ERROR!! NO PRICE!! %s" % response.url
                continue
            price = price[0]

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)

            loader.add_value('sku', '')

            yield loader.load_item()

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)

        url = response.url
        name = hxs.select('//div[@id="package_showcase"]/div[@id="description"]/h1/text()')[0].extract()
        if not name:
            print "ERROR!! NO NAME!! %s" % url
        name = name[0].split(" - Home Delivered")
        price = hxs.select('//div[@id="package_showcase"]/div[@id="pricing"]/strong[last()]/text()')[-1].extract()
        if not price:
            print "ERROR!! NO PRICE!! %s" % url
        price = price[0]

        product = Product()
        loader = ProductLoader(item=product, response=response)
        loader.add_value('url', url)
        loader.add_value('name', name)
        loader.add_value('price', price)

        loader.add_value('sku', '')

        yield loader.load_item()

