from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.http.cookies import CookieJar
from scrapy import log

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class PecheurSpider(BaseSpider):
    name = 'pecheur.com'
    allowed_domains = ['pecheur.com']
    start_urls = ('http://www.pecheur.com',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        cats = hxs.select('//ul[contains(@class, "barre-navigation")]//a/@href').extract()
        for cat in cats:
            yield Request(urljoin_rfc(get_base_url(response), cat), callback=self.parse_subcategories)

    def parse_subcategories(self, response):
        hxs = HtmlXPathSelector(response)

        sub_cats = hxs.select('//div[@class="colonne_gauche"]/div[@id="menu"]//ul/li/a/@href').extract()
        for sub_cat in sub_cats:
            yield Request(urljoin_rfc(get_base_url(response), sub_cat), callback=self.parse_subcategories)

        next_page = hxs.select('//div[@class="droite"]/a/@href').extract()
        if next_page:
            yield Request(urljoin_rfc(get_base_url(response), next_page[0]), callback=self.parse_subcategories)

        for product in self.parse_products(hxs, response):
            yield product

    def parse_products(self, hxs, response):
        products = hxs.select('//li[@class="article"]')

        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', './/span[@class="nom"]/text()')

            price = product.select('.//span[contains(@class, "prix")]/span[position() < last()]/text()').extract()
            price = "".join(price).replace(',', '.').strip()

            loader.add_value('price', price)
            url = product.select('./a/@href').extract()[0]
            url = urljoin_rfc(get_base_url(response), url)
            loader.add_value('url', url)

            yield loader.load_item()
