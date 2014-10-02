import functools

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
def first(s):
    if isinstance(s, list) and s:
        return s[0]
    return s

class HdewcamerasCoUkSpider(BaseSpider):
    name = 'hdewcameras.co.uk-procamerashop'
    allowed_domains = ['rtrk.co.uk', ]
    start_urls = ('http://hdewcameras1-px.rtrk.co.uk/sitemap.asp',)

    categories_xpath = "/html/body/div[1]/div/div[2]/div[2]/ul/li/a/@href"
    categories_nextpage_xpath = None
    products_xpath = "/html/body/div[1]/div/div[2]/div[2]/div[4]/div[@class='products']/div[@class='row']"
    products_nextpage_xpath = "//a/b/../@href"

    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # TODO: categories_nextpage_xpath

        if self.categories_xpath:
            categories = hxs.select(self.categories_xpath).extract()
            for url in categories:
                yield Request(urljoin_rfc(base_url, url), callback=self.parse_page)


    def parse_page(self, response):
        base_url = get_base_url(response)
        base_url_func = functools.partial(urljoin_rfc, base_url)
        hxs = HtmlXPathSelector(response)

        # products next page
        if self.products_nextpage_xpath:
            url = hxs.select(self.products_nextpage_xpath).extract()
            if url:
                yield Request(urljoin_rfc(base_url, url[0]), callback=self.parse_page)

        # products
        if self.products_xpath:
            for z in hxs.select(self.products_xpath):
                loader = ProductLoader(selector=z, item=Product())
                loader.add_xpath('name', "./div[@class='description']/span/a/text()")
                loader.add_xpath('url', "./div[@class='description']/span/a/@href", first, base_url_func)
                loader.add_xpath('price', "./div[@class='price']/text()")

                yield loader.load_item()

