import os
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.fuzzywuzzy import process
from product_spiders.fuzzywuzzy import fuzz

HERE = os.path.abspath(os.path.dirname(__file__))

class StrawberryNetSpider(BaseSpider):
    name = 'cocopanda-strawberrynet.com'
    allowed_domains = ['strawberrynet.com']
    start_urls = ['http://no.strawberrynet.com/shop-by-brand/']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        brands = hxs.select('//div[@id="divLeftIndex"]/a')
        for a in brands:
            brand = a.select('text()').extract()[0]
            url = a.select('@href').extract()[0]
            request = Request(urljoin_rfc(base_url, url), callback=self.parse_brand)
            yield request

    def parse_brand(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)
        brand = ' '.join(hxs.select('//h1[@id="lbTitle"]/text()[1]').extract())

        other_types = hxs.select('//div[@class="prodpromoLeft"]//a/@href').extract()
        for url in other_types:
            yield Request(urljoin_rfc(base_url, url), callback=self.parse_brand)

        products = hxs.select('//div[@class="row" or @class="row rowcolor"]')

        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            name = ' '.join(product.select('.//a[@class="whitebglink"]/text()').extract())
            loader.add_value('name', ' '.join((brand, name)))
            price = ''.join(product.select('div[@class="col4 cols"]/div/span/text()').extract()).replace(',','.').replace('\r','').replace(' ','')
            loader.add_value('price', price)
            
            product_url = product.select('.//a[@class="whitebglink"]/@href').extract()[0]
            loader.add_value('url', urljoin_rfc(base_url, product_url))
            loader.add_xpath('sku', './/a[@name]/@name')
            yield loader.load_item()

