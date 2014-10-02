from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader


class JohnLewisSpider(BaseSpider):
    name = 'johnlewis.com-travel'
    allowed_domains = ['johnlewis.com']
    start_urls = ['http://www.johnlewis.com/Shop+by+Brand/Antler/Antler/SubCategory.aspx',
                  'http://www.johnlewis.com/Shop+by+Brand/Eastpak/Category.aspx',
                  'http://www.johnlewis.com/Shop+by+Brand/Samsonite/Category.aspx',
                  'http://www.johnlewis.com/Wenger/Brand.aspx']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories =  hxs.select('//*[@id="LHNCtl1_rptGp_ctl00_LHNGpCtl1_subnavac"]/ul/li/a/@href').extract()
        if categories:
            for category in categories:
                url =  urljoin_rfc(get_base_url(response), category)
                yield Request(url, callback=self.parse_products)
        else:
            yield Request(response.url, dont_filter=True, callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//*[@id="SearchResultsGrid1_UpdatePanel1"]/div/div[@class="grid-item"]') 
        if products:
            for product in products:
                loader = ProductLoader(item=Product(), selector=product)
                loader.add_xpath('name', 'div[@class="grid-copy"]/a[@class="gridtitle"]/text()')
                url = urljoin_rfc(get_base_url(response), product.select('div[@class="grid-copy"]/a[@class="gridtitle"]/@href').extract()[0])
                loader.add_value('url', url)
                price = ''.join(product.select('div[@class="grid-copy"]/a[@class="price"]/text()').extract()).split()[-1]
                loader.add_value('price', price)
                yield loader.load_item()

