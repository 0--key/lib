from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

class FoodServiceWarehouseSpider(BaseSpider):
    name = 'foodservicewarehouse.com'
    allowed_domains = ['foodservicewarehouse.com']
    start_urls = ('http://www.foodservicewarehouse.com',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        cats = hxs.select('//table[@id="tbl_Tabs"]//a/@href').re('(.*/c\d+\.aspx)')
        cats += hxs.select('//div[starts-with(@class, "I1")]//a[not(@class)]/@href').extract()
        cats += hxs.select('//div[@class="I2b"]/a/@href').extract()
        cats += hxs.select('//div[@class="NW2"]//td//a/@href').re('(.*/c\d+\.aspx)')
        cats += hxs.select('//a[contains(@id, "pager_lnk")]/@href').re('(.*/\d+\.aspx)')
        cats += hxs.select('//div[@class="PAG"]/a/@href').extract()
        cats += hxs.select('//div[@class="cat"]/a/@href').extract()
        for cat in cats:
            yield Request(urljoin_rfc(get_base_url(response), cat))

        for product in self.parse_products(response, hxs):
            yield product

    def parse_products(self, response, hxs):
        products =  hxs.select('//div[@class="WG1"]/..')
        for product in products:
            loader = ProductLoader(selector=product, item=Product())
            url =  product.select('.//a/@href').re('p\d+\.aspx')[0]
            url = urljoin_rfc(get_base_url(response), url)
            loader.add_value('url', url)
            loader.add_xpath('name', './/a/text()')
            loader.add_xpath('sku', './/a/text()', re='.*\((.*)\).*')
            loader.add_xpath('price', './/h2/text()')
            yield loader.load_item()

        products = hxs.select('//table[@class="J5"]//div[@class="is"]/..')
        for product in products:
            loader = ProductLoader(selector=product, item=Product())
            url =  product.select('.//a/@href').re('p\d+\.aspx')[0]
            url = urljoin_rfc(get_base_url(response), url)
            loader.add_value('url', url)
            loader.add_xpath('name', './/a/text()')
            loader.add_xpath('sku', './/a/text()', re='.*\((.*)\).*')
            loader.add_xpath('price', './/div[@class="is"]/text()')
            yield loader.load_item()
