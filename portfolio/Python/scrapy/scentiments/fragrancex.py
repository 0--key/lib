import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

from scrapy import log

class FragrancexSpider(BaseSpider):
    name = 'fragrancex.com'
    allowed_domains = ['fragrancex.com']
    start_urls = ('http://www.fragrancex.com/products/allbrands.html',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        categories = hxs.select('//td[@class="c_tablefill"]//a[starts-with(@id, "rpAllBrands")]/@href').extract()

        for cat in categories:
            yield Request(urljoin_rfc(get_base_url(response), cat), callback=self.parse_categories)


    def parse_categories(self, response):
        hxs = HtmlXPathSelector(response)

        categories = hxs.select('//a[starts-with(@id, "rpBrandCategories")]/@href').extract()

        for cat in categories:
            yield Request(urljoin_rfc(get_base_url(response), cat), callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)

        products = hxs.select('//tr[contains(@id, "ProductRow")]')

        for p in products:
            loader = ProductLoader(item=Product(), selector=p)
            loader.add_value('url', response.url)
            name1 = ' '.join(p.select('.//td[2]/span/text()').extract())
            name2 = ' '.join(p.select('.//td[3]/span/text()').extract())
            name = name1 + ' ' + name2
            name = re.sub(' +', ' ', name)

            loader.add_value('name', name)
            loader.add_xpath('price', './/td[contains(@class, "OurPrice")]/span/text()')

            yield loader.load_item()

