from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

class FireplaceworldCoUkSpider(BaseSpider):
    name = 'fireplaceworld.co.uk'
    allowed_domains = ['fireplaceworld.co.uk']
    start_urls = ('http://www.fireplaceworld.co.uk',)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)

        url = response.url

        #name = hxs.select('//div[@id="package_showcase"]/div[@id="description"]/h1/text()').extract()
        name = hxs.select('//h1[@itemprop="name"]/text()').extract()
        if not name:
            print "ERROR!! NO NAME!! %s" % url
            return
        name = name[0]

        #price = hxs.select('//div[@id="package_showcase"]/div[@id="pricing"]/strong[last()]/text()').extract()
        price = hxs.select('//span[@itemprop="price"]/text()').extract()
        if not price:
            print "ERROR!! NO PRICE!! %s" % url
            return
        price = price[-1]

        product = Product()
        loader = ProductLoader(item=product, response=response)
        loader.add_value('url', url)
        loader.add_value('name', name)
        loader.add_value('price', price)

        loader.add_value('sku', response.url.split('/')[-2])

        yield loader.load_item()

    def parse(self, response):
        URL_BASE = get_base_url(response)
        #categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//div[@id="site_header_nav"]/ul/li[position()!=last()]//a/@href').extract()
        category_urls += hxs.select('//span[@class="page-numbers"]//a/@href').extract()
        for url in category_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        #product_urls = hxs.select('//div[@id="packages"]/div[contains(@class, "package")]/a/@href').extract()
        product_urls = hxs.select('//div[@class="package-details"]/h2/a/@href').extract()
        for url in product_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url, callback=self.parse_product)
