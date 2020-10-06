from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class InstawaresSpider(BaseSpider):
    name = 'instawares.com'
    allowed_domains = ['instawares.com']
    start_urls = ('http://www.instawares.com/',)
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5'

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        '''
        #categories
        cats = hxs.select('//ol[@class="mainNavOL"]//a/@href').extract()
        #subcategories
        cats += hxs.select('//h2[@class="superCatH2"]/following-sibling::ol//a/@href').extract()
        #sub subcategories
        cats += hxs.select('//ol[@class="subCatList"]//a/@href').extract()
        '''
        cats = ['http://www.instawares.com/winco-d-w-l-.0.485.0.0.htm',
                'http://www.instawares.com/cardinal-brands-inc.0.1062.0.0.htm',
                'http://www.instawares.com/libbey-glassware.0.214.0.0.htm',
                'http://www.instawares.com/victory-refrigeration-company.0.566.0.0.htm',
                'http://www.instawares.com/vollrath.0.4062.0.0.htm',
                'http://www.instawares.com/dexter-russell.0.304.0.0.htm',
                'http://www.instawares.com/f-dick.0.2107.0.0.htm',
                'http://www.instawares.com/cecilware.0.668.0.0.htm',
                'http://www.instawares.com/turbo-air.0.1664.0.0.htm',
                'http://www.instawares.com/eastern-tabletop.0.2081.0.0.htm',
                'http://www.instawares.com/get-enterprises-inc.0.150.0.0.htm',
                'http://www.instawares.com/emi-yoshi.0.2428.0.0.htm',
                'http://www.instawares.com/beverage-air-.0.659.0.0.htm',
                'http://www.instawares.com/amana.0.2029.0.0.htm',
                'http://www.instawares.com/bakers-pride.0.604.0.0.htm']
        #next page
        cats += hxs.select('//a[@id="tmiwapi-nav-link-next"]/@href').extract()
        cats += hxs.select('//td[@class="tableHeaderText"]/a/@href').extract()
        cats += hxs.select('//a[@class="tableHeaderText"]/@href').extract()
        for cat in cats:
            yield Request(urljoin_rfc(get_base_url(response), cat))

        products = hxs.select('//td[@id="searchresults_list" and @class="regularTxt_small"]//a/@href').extract()
        products += hxs.select('//td[@class="details"]//a/@href').extract()
        for url in products:
            yield Request(urljoin_rfc(get_base_url(response), url), callback=self.parse_product)

    def parse_product(self, response):
        loader = ProductLoader(response=response, item=Product())
        loader.add_value('url', response.url)
        loader.add_xpath('name', '//h1[@class="productName fn"]/text()')
        loader.add_xpath('price', '//li[@class="price"]//text()')
        loader.add_xpath('sku', '//div[starts-with(@class, "specificationContent")]' +
                                '//td[contains(text(), "Manufacturer ID")]/following-sibling::td/text()')

        yield loader.load_item()
