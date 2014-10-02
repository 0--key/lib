import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class DolphinMusicSpider(BaseSpider):
    name = 'dolphinmusic.co.uk'
    allowed_domains = ['dolphinmusic.co.uk']
    start_urls = ['http://www.dolphinmusic.co.uk/']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        relative_urls = hxs.select('//*[@id="sidebar"]/ul[@class="drilldown"]/li/a/@href').extract()
        for relative_url in relative_urls:
            url = urljoin_rfc('http://www.dolphinmusic.co.uk/',
                              relative_url, response.encoding)

            yield Request(url, callback=self.parse_categories)

    def parse_categories(self, response):
        hxs = HtmlXPathSelector(response)
        relative_urls = hxs.select('//*[@id="sidebar"]/ul[@id="refineCat"]/li/a/@href').extract()
        for relative_url in relative_urls:
            url = urljoin_rfc('http://www.dolphinmusic.co.uk/',
                              relative_url, response.encoding)
            yield Request(url, callback=self.parse_page)


    def parse_page(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="item"]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', 'h2/a/text()')
            relative_url = product.select('h2/a/@href').extract()[0]
            url = urljoin_rfc('http://www.dolphinmusic.co.uk/', 
                              relative_url, response.encoding)
            loader.add_value('url', url)
            loader.add_xpath('price', 'div[@class="pricing"]/p[@class="price"]/text()')
            yield loader.load_item()
        next_page = hxs.select('//*[@id="categoryMain"]/div[@class="pagination"]/ul/li/a/@href').extract()
        if not next_page:
            relative_urls = hxs.select('//*[@id="sidebar"]/ul[@id="refineCat"]/li/a/@href').extract()
            for relative_url in relative_urls:
                url = urljoin_rfc('http://www.dolphinmusic.co.uk/',
                                  relative_url, response.encoding)
                yield Request(url, callback=self.parse_page)
        else:
            next_url = next_page[-1]
            if self._is_next(next_url):
                url = urljoin_rfc('http://www.dolphinmusic.co.uk/',
                                   next_url, response.encoding)
                yield Request(url, callback=self.parse_page)

    def _is_next(self, next_url):
        return re.findall(r'\d+', next_url) 

