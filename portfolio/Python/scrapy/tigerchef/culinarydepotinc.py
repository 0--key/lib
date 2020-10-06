from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader


class CulinaryDepotIncSpider(BaseSpider):
    name = 'culinarydepotinc.com'
    allowed_domains = ['culinarydepotinc.com']
    start_urls = ('http://www.culinarydepotinc.com',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        base_url = get_base_url(response)
        categories = hxs.select('//ul[@class="tame"]/li/a/@href').extract()
        for category in categories:
            yield Request(urljoin_rfc(base_url, category), cookies={'pagesize': 10000})

        next_page = hxs.select('//li[@class="pagingPreviousNext"]/a[starts-with(text(), "Next")]/@href').extract()
        if next_page:
            yield Request(urljoin_rfc(base_url, next_page[0]))

        for product in self.parse_products(hxs, base_url):
            yield product

    def parse_products(self, hxs, base_url):
        products = hxs.select('//div[@class="productResultInfo"]')
        for product in products:
            product_loader = ProductLoader(Product(), product)
            product_loader.add_xpath('name', './/a[@class="ProductNameText"]/text()')
            url = product.select('.//a[@class="ProductNameText"]/@href').extract()[0]
            product_loader.add_value('url', urljoin_rfc(base_url, url))
            price = ' '.join(product.select('.//span[@class="variantprice"]//text()').extract())
            product_loader.add_value('price', price)
            product_loader.add_xpath('sku', './/p[contains(@class, "productSKU")]/text()')
            yield product_loader.load_item()
