from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class HuntinglifeNetSpider(BaseSpider):
    name = 'huntinglife.net'
    allowed_domains = ['huntinglife.net']
    start_urls = ('http://webshop.huntinglife.net/shop.aspx',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//div[@class="lm_catalog"]/ul/li/ul/li/a/@href').extract():
            yield Request(url, callback=self.parse_product)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        for item in hxs.select(u'//td/div[contains(@class,"ProductDisplayList")]'):
            product_loader = ProductLoader(item=Product(), selector=item)

            product_loader.add_xpath('name', u'.//div[@class="ProductDisplayList_Name"]/a/text()')

            price = item.select(u'.//span[@class="price"]/text()').extract()[0]
            price = price.strip().lstrip('DKK ').replace('.', '').replace(',', '.')
            product_loader.add_value('price', price)

            product_loader.add_xpath('url', u'.//div[@class="ProductDisplayList_Name"]/a/@href')

            product = product_loader.load_item()
            # Product page contains the full name,
            # list has something shorter without important information like caliber
            yield Request(product['url'], meta={'product':product}, callback=self.parse_product_name)

    def parse_product_name(self, response):
        hxs = HtmlXPathSelector(response)
        product = response.meta['product']
        product['name'] = hxs.select(u'//h1/text()').extract()[0].strip()
        yield product
