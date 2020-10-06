# scrapy includes
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy import log

# spider includes
from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

# main class
class ReliefMartSpider(BaseSpider):

    # setup
    name = "reliefmart.com" # Name must match the domain
    allowed_domains = ["reliefmart.com"]
    # start_urls = ["http://www.medlief.com/sitemap.html",]
    start_urls = ["http://www.reliefmart.com/products.htm",]

    # main request
    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        #categoryUrls = hxs.select("//table[@id='table3']//td[1]//img/../@href").extract()
        categoryUrls = hxs.select("//table[@id='table3']//a/@href").extract()
        for categoryUrl in categoryUrls:
            yield Request(urljoin_rfc(base_url, categoryUrl), callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)

        #products = hxs.select("//input[@src='bluo-add.gif']/../..")
        products = hxs.select("//input[@src='bluo-add.gif']/ancestor::form")

        for product in products:
            product_info = product.select(".//input[starts-with(@name, 'item') and " +
                                          "not(contains(@name, 'source'))]/@value").extract()

            if not product_info:
                for p in self.parse_composite_products(product, response.url, response):
                    yield p

                continue

            product_info = product_info[0]
            name, price = product_info.split('^')[2:4]
            sub_products = product.select('.//option[@value="0"]//following-sibling::option/text()').extract()

            if sub_products:
                log.msg('Subproducts on %s' % response.url)
                for p in sub_products:
                    loader = ProductLoader(item=Product(), response=response)
                    loader.add_value('url', response.url)
                    loader.add_value('name', name + ' ' + p)
                    loader.add_value('price', price)

                    yield loader.load_item()

            else:
                loader = ProductLoader(item=Product(), response=response)
                loader.add_value('url', response.url)
                loader.add_value('name', name)
                loader.add_value('price', price)

                yield loader.load_item()

    def parse_composite_products(self, product, url, response):
        # sub_products = product.select('.//select[@name="item"]/option/@value').extract()
        sub_products = product.select('.//select[starts-with(@name, "item")]/option/@value').extract()
        for p in sub_products:
            name, price = p.split('^')[2:4]
            loader = ProductLoader(item=Product(), response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)

            yield loader.load_item()

