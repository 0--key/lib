from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader


class Phones4uSpider(BaseSpider):
    name = 'phones4u.co.uk'
    allowed_domains = ['phones4u.co.uk']
    start_urls = ['http://www.phones4u.co.uk/shop/shop_payg_main.asp?intcid=PAYG%20Phones']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//*[@id="secBody"]/table/tbody/tr/td/a/@href').extract()
        for category in categories:
            url = urljoin_rfc(response.url, category.strip(), response.encoding)
            yield Request(url, callback=self.parse_pages)

    def parse_pages(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//*[@id="manphones"]/table/tbody/tr[not(@class="netempty")]/td[not(@class="manempty")]')
        for product in products:
            BASE_URL = 'http://www.phones4u.co.uk/'
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', 'a/text()')
            relative_url = product.select('a/@href').extract()[0]
            url = urljoin_rfc(BASE_URL, relative_url, response.encoding)
            loader.add_value('url', url)
            loader.add_xpath('price', 'text()')
            yield loader.load_item()
