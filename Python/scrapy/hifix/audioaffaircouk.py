import logging

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader


class AudioaffairCoUkSpider(BaseSpider):
    name = 'audioaffair.co.uk'
    allowed_domains = ['audioaffair.co.uk']
    start_urls = ('http://audioaffair.co.uk',)

    def parse(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # categories
        category_urls = hxs.select('//div[@id="categorytreeleft"]/ul/li//a/@href').extract()
        for url in category_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        # pages
        pages_urls = hxs.select('//div[@class="pagination"]//a/@href').extract()
        for url in pages_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        # products list
        products = hxs.select("//table[@class='tblList']/tr")
        if not products:
            logging.error("ERROR!! NO PRODUCTS!! %s " % response.url)
        for product_el in products:
            name = product_el.select("td[2]/a[@class='txtDefaultCatTitle']//text()").extract()
            if not name:
                continue
            name = name[0]

            url = product_el.select("td[2]/a[@class='txtDefaultCatTitle']/@href").extract()
            if not url:
                logging.error("ERROR!! NO URL!! %s %s" % (response.url, name))
                continue
            url = url[0]
            url = urljoin_rfc(URL_BASE, url)

            price = product_el.select("td[3]/div/div[@class='txtDefaultPrice']//text()").extract()
            if not price:
                logging.error("ERROR!! NO PRICE!! %s %s" % (response.url, name))
                continue

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)
            yield loader.load_item()
