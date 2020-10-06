import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

class TyresCoUk(BaseSpider):
    name = '4x4tyres.co.uk'
    allowed_domains = ['4x4tyres.co.uk', 'www.4x4tyres.co.uk']
    start_urls = ('http://www.4x4tyres.co.uk',)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        # categories
        category_urls = hxs.select(u'//div[@id="categoryTab"]//a/@href').extract()
        for url in category_urls:
            yield Request(url)

        # subcategories
        subcategories_urls = hxs.select(u'//div[@id="thecategories"]//a/@href').extract()
        for url in subcategories_urls:
           yield Request(url)


        # pagination
        # next_page = hxs.select(u'').extract()
        # if next_page:
        #     url = urljoin_rfc(URL_BASE, next_page[0])
        #   yield Request(url)

        # products
        product_urls = hxs.select(u'//div[@class="listingBox"]//div[@class="headergrid"]//a/@href').extract()
        for url in product_urls:
            yield Request(url, callback=self.parse_product)

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        product_loader = ProductLoader(item=Product(), response=response)
        product_loader.add_xpath('name', u'//form/div[not(@class)]/h1[not(@class)]/text()')
        product_loader.add_value('url', response.url)
        product_loader.add_xpath('price', u'//form//div[@class="contentText"]//div[@class="PriceList"]/div[@class="pricenow"]/text()', re=u'\xa3(.*)')
        product_loader.add_xpath('sku', u'//td[@class="ProductPageSummaryTableInfo" and preceding-sibling::td[@class="ProductPageSummaryTable" and contains(text(),"Model Number")]]/text()')
        yield product_loader.load_item()
