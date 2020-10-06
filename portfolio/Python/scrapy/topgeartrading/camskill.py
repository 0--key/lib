import re

from decimal import Decimal

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product

class CamskillCoUk(BaseSpider):
    name = 'camskill.co.uk'
    allowed_domains = ['camskill.co.uk', 'www.camskill.co.uk']
    start_urls = ('http://camskill.co.uk/products.php',)

    def __init__(self, *args, **kwargs):
        super(CamskillCoUk, self).__init__(*args, **kwargs)
        self.URL_BASE = 'http://camskill.co.uk'

    def parse_product(self, response):
        
        hxs = HtmlXPathSelector(response)

        products = hxs.select('//form[@name="priceMatch"]/../..')

        for p in products:
            res = {}
            try:
                name =  p.select('.//a/text()').extract()[0]
                url = p.select('.//a/@href').extract()[0]
                url = urljoin_rfc(self.URL_BASE, url)

                price = p.re('OFFER \xa3(.*)</b')

                if not price:
                    price = p.re('OUR PRICE \xa3(.*) <') # if there isn't a special offer

                price = price[0] if price else '0'

                res['url'] = url
                res['description'] = name
                price = Decimal(price) + Decimal(3)
                price = str(price)
                res['price'] = price
                yield load_product(res, response)
            except IndexError:
                return


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        # categories
        if response.url == self.start_urls[0]:
            category_urls = hxs.select('//table//table//table//td//a[contains(text(),"4x4") or contains(text(),"4X4")]/@href').extract()
            for url in category_urls:
                url = urljoin_rfc(self.URL_BASE, url)
                yield Request(url)

        # subcategories
        subcategories_urls = hxs.select('//div[@class="subCategoryEntry"]/a/@href').extract()
        for url in subcategories_urls:
           url = urljoin_rfc(self.URL_BASE, url)
           yield Request(url, callback=self.parse_product)


        #next page
        # next_page =
        # if next_page:
        #     url = urljoin_rfc(self.URL_BASE, next_page[0])
        #   yield Request(url)
