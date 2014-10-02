from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class ReidysSpider(BaseSpider):
    name = 'reidys.com'
    allowed_domains = ['reidys.com']
    start_urls = ['http://www.reidys.com/']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        urls = hxs.select('//div[@class="menu_wrap"]/div/div/div/a/@href').extract()
        for url in urls:
            yield Request(url, callback=self.parse_categories)

    def parse_categories(self, response):
        hxs = HtmlXPathSelector(response)
        sub_categories = hxs.select('//div[@class="section_190"]/a/@href').extract()
        if not sub_categories:
            products = hxs.select('//div[@class="list_search_result"]')
            for product in products:
                loader = ProductLoader(item=Product(), selector=product)
                loader.add_xpath('name', 'div[@class="list_search_detail"]/'
                                         'div[@class="list_search_info"]/p/a/'
                                         'span/text()')
                loader.add_xpath('url', 'div[@class="list_search_detail"]/'
                                        'div[@class="list_search_info"]/p/a/@href')
                loader.add_xpath('price', 'div[@class="list_search_detail"]/'
                                          'div[@class="list_search_actionblock"]/'
                                          'p/span[@class="list_search_price"]/text()')
                yield loader.load_item()
            next_page = hxs.select('//div[@class="formfloatright"]/'
                                   'strong/a[text()="Next>"]/@href').extract()
            if next_page:
                next_url = next_page[-1]
                yield Request(next_url, callback=self.parse_categories)
        else:
            urls = hxs.select('//div[@class="section_190"]/a/@href').extract()
            for url in urls:
                yield Request(url, callback=self.parse_categories)

