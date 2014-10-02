import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class ProCameraShopSpider(BaseSpider):
    name = "procamerashop.com"
    allowed_domains = ["procamerashop.co.uk", "www.procamerashop.co.uk"]
    start_urls = ("http://www.procamerashop.co.uk/frontend/siteMap",)

    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        cat_urls = hxs.select('//div[@id="sitemapCategoryTree"]/ul/li/a/@href').extract()

        for cat_url in cat_urls:
            yield Request(urljoin_rfc(base_url, cat_url), callback=self.parse_category)

    def parse_category(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        product_urls = hxs.select('//div[@class="productTable"]/table//tr[contains(@id,"tr_")]/td[2]/a/@href').extract()
        for product_url in product_urls:
            yield Request(urljoin_rfc(base_url, product_url), callback=self.parse_product)

        next_page = hxs.select('//div[@class="pagination"]/ul/li/a[contains(text(),"Next")]/@href').extract()
        if(next_page):
            yield Request(urljoin_rfc(base_url, next_page[0]), callback=self.parse_category)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        loader = ProductLoader(response=response, item=Product())
        loader.add_value('url', response.url)
        loader.add_xpath('name', '//div[@id="productDetail"]//h1[@class="productDetailTitle"]/text()')
        loader.add_xpath('price', '//div[@id="productDetail"]//span[contains(@class,"price")]/text()')
        sku = hxs.select('//div[@id="productDetail"]//p[1]')[0].re('Ref\. Code: (\d+)')
        loader.add_value('sku', sku)

        yield loader.load_item()
