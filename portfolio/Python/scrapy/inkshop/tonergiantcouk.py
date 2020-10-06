import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from productloader import load_product


from scrapy.http import FormRequest

class TonerGiant(BaseSpider):
    name = 'tonergiant.co.uk'
    allowed_domains = ['tonergiant.co.uk', 'www.tonergiant.co.uk']
    start_urls = ('http://www.tonergiant.co.uk/catalogue/Select-By-Brand-1067/',)
    
    def __init__(self, *args, **kwargs):
        super(TonerGiant, self).__init__(*args, **kwargs)
        self.URL_BASE = 'http://www.tonergiant.co.uk'
        
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        res = {}
        name = hxs.select('.//span[@id="productInformationHeaderReference"]/text()').extract()[0]
        url = response.url
        price = hxs.select('.//div[@class="AXISBreakPricing1"]/div[@class="AXISBreakPricingPrice"]').re("\xa3(.*)<")[0]
        res['url'] = url
        res['description'] = name
        res['price'] = price
        res['sku'] = res['description']
        yield load_product(res, response)


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        #categories
        hxs = HtmlXPathSelector(response)
        # printer brands
        printers_brands = hxs.select('//div[@id="catalogueDirectory"]//img[@class="catalogueImage"]/../@href').extract()
        for url in printers_brands:
            url = urljoin_rfc(self.URL_BASE, url)
            yield Request(url)

        printers_series = hxs.select('//div[@id="printerWizardFamilyContainer" or @id="printerWizardModelContainer"]//a/@href')\
                             .extract()
        for url in printers_series:
            url = urljoin_rfc(self.URL_BASE, url)
            yield Request(url)

        # next page
        next_page = hxs.select('//a[@class="AXISPageNumber" and contains(text(),"Next")]/@href').extract()
        if next_page:
            url = urljoin_rfc(self.URL_BASE, next_page[0])
            yield Request(url)

        # products
        products = hxs.select('//tr[contains(@class,"productList")]//h3[@class="productListItemHeader"]/a/@href').extract()
        for product in products:
            product = urljoin_rfc(self.URL_BASE, product)
            yield Request(product, callback=self.parse_product)