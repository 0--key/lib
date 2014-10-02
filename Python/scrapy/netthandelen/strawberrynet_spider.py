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
    name = 'strawberrynet.com'
    allowed_domains = ['strawberrynet.com']
    start_urls = ['http://no.strawberrynet.com/shop-by-brand/']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//*[@id="menuInner"]/ul/li/a/@href').extract()
        for category in categories:
            url =  urljoin_rfc(get_base_url(response), category)
            yield Request(url, callback=self.parse_categories)

    def parse_categories(self, response):
        hxs = HtmlXPathSelector(response)
        brands = hxs.select('//div[@class="brandNDG"]/a[@class]')
        if not brands:
            brands =  hxs.select('//div[@class="branditems"]/a')
        for brand in brands:
            url =  urljoin_rfc(get_base_url(response), brand.select('@href').extract()[0])
            brand_name = brand.select('text()').extract()[0]
            yield Request(url, callback=self.parse_brand, meta={'brand': brand_name})

    #def parse_brands(self, response):
    #    hxs = HtmlXPathSelector(response)
    #    brands = hxs.select('//div[@class="brandDiv"]/a/@href').extract()
    #    for brand in brands:
    #        url =  urljoin_rfc(get_base_url(response), brand)
    #        yield Request(url, callback=self.parse_products)

    def parse_brand(self, response):
        hxs = HtmlXPathSelector(response)
        brand = response.meta['brand']
        products = hxs.select('//div[@class="row" or @class="row rowcolor"]')
        for product in products:
            relative_url =  ''.join(product.select('div[@class="col1 cols"]/a/@href').extract())
            options = ''.join(product.select('div[@class="col2 cols"]/a[not(@class="imgLink" or @class="whitebglink")]/@href').extract())
            if options:
                yield Request(urljoin_rfc(get_base_url(response), options), callback=self.parse_brand, meta={'brand': brand})
            else:
                loader = ProductLoader(item=Product(), selector=product)
                name = ' '.join(''.join(product.select('div[@class="col1 cols"]/a/text()').extract()).split())
                if not name:
                    name = ' '.join(''.join(product.select('div[@class="col1 cols"]/a/p/text()').extract()).split())
                loader.add_value('name', ' '.join((brand, name)))
                loader.add_value('url', urljoin_rfc(get_base_url(response), relative_url))
                price = ''.join(product.select('div[@class="col4 cols"]/div/span/text()').extract()).replace(',','.').replace('\r','').replace(' ','')
                loader.add_value('price', price)
                yield loader.load_item()
