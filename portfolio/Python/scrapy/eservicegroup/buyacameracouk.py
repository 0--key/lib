import logging

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

class BuyacameraCoUkSpider(BaseSpider):
    name = 'buyacamera.co.uk'
    allowed_domains = (
        'buyacamera.co.uk',
    )
    start_urls = (
        "http://www.buyacamera.co.uk",
        "http://www.buyacamera.co.uk/search.asp?sort=CA,DC",
        "http://www.buyacamera.co.uk/search.asp?searchtype=name&searchfor=canoneos",
        "http://www.buyacamera.co.uk/search.asp?searchtype=name&searchfor=nikond",
        "http://www.buyacamera.co.uk/search.asp?searchtype=name&searchfor=lumixg",
        "http://www.buyacamera.co.uk/search.asp?searchtype=name&searchfor=sonyalpha",
    )

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        categories = hxs.select("//body/center/table[2]/tr[1]/td[1]/table[1]//a/@href").extract()
        for url in categories:
            yield Request(
                    url=self._urljoin(response, url)
                    )
        hxs = HtmlXPathSelector(response)

        products = hxs.select("//body/center/table[2]/tr[1]/td[2]/table[1]/tr | \
                               //body/table[2]/tr[1]/td[2]/table[3]/tr")
        for product in products:
            name = product.select(
                    "td[2]/table/tr[1]/td/a/text()"
                    ).extract()
            if not name:
                logging.error("Name not found!")
                continue
            name = name[0]

            url = product.select(
                    "td[2]/table/tr[1]/td/a/@href"
                    ).extract()
            if not url:
                logging.error("Url not found!")
                continue
            url = self._urljoin(response, url[0])

            price = product.select(
                    "td[3]/font[1]/b/text()"
                    ).extract()
            if not price:
                logging.error("Price not found!")
                continue
            price = price[0]

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)
            yield loader.load_item()


    def _urljoin(self, response, url):
        return urljoin_rfc(get_base_url(response), url)


