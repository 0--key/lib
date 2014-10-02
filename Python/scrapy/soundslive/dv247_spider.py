from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class Dv247Spider(BaseSpider):
    name = 'dv247.com-soundslive'
    allowed_domains = ['dv247.com', 'www.dv247.com']
    start_urls = ('http://www.dv247.com/sitemap',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        relative_urls = hxs.select('//*[@id="form1"]/ul/li/a/@href').extract()
        for relative_url in relative_urls:
            url = urljoin_rfc('http://www.dv247.com/',
                              relative_url, response.encoding)
            yield Request(url, callback=self.parse_categories) 

    def parse_categories(self, response):
        hxs = HtmlXPathSelector(response)
        relative_urls = hxs.select('//*[@id="menu"]/div/ul/li/ul/li/a/@href').extract()
        for relative_url in relative_urls:
            url = urljoin_rfc('http://www.dv247.com/',
                              relative_url, response.encoding)
            yield Request(url, callback=self.parse_pagination) 

    def parse_pagination(self, response):
        URL_BASE = 'http://www.dv247.com/'

        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="listItem clearfix"]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            name = ''.join(product.select('.//a//text()').extract())
            loader.add_value('name', name)
            relative_url = product.select('.//a/@href')[0].extract()
            url = urljoin_rfc(URL_BASE, relative_url)
            loader.add_value('url', url)
            loader.add_xpath('price', './/li[@class="price"]/text()')
            yield loader.load_item()
        
        #next page
        next_pages = hxs.select('//div[@class="listPaging"]')
        next_ten = []
        if next_pages:
            next_ten = next_pages[0].select('.//a[text()="Next 10"]/@href').extract()
        
        if next_pages:
            next_pages = next_pages[0].select('.//a[not(@class="selectedpage") and not(text()="Next 10") and not(text()="Previous 10")]/@href').extract()
            for page in next_pages:
                url = urljoin_rfc(URL_BASE, page)
                yield Request(url, callback=self.parse_pagination)

        if next_ten:
            next_ten_url = urljoin_rfc(URL_BASE, next_ten[0])
            yield Request(next_ten_url, callback=self.parse_pagination)
      






