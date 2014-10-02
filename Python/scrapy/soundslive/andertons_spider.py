from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class AnderstonSpider(BaseSpider):
    name = 'andertons.co.uk'
    allowed_domains = ['music.andertons.co.uk']
    #Empty search to obtain all the articles.
    start_urls = ['http://music.andertons.co.uk/search?w=&nodet=1']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//a[@class="prod-box"]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', 'span[@class="prod-desc-area"]/'
                                     'span[@class="prod-name-row"]/strong/text()')
            loader.add_xpath('url','@href')
            loader.add_xpath('price', 'span[@class="prod-desc-area"]/'
                                      'span[@class="price-prod"]/text()')
            yield loader.load_item()
        
        next_page =  hxs.select('//*[@id="sli_pagination_footer"]/'
                                'span/a[text()="Next"]/@href').extract()
        if next_page:
            next_url = next_page[-1]
            yield Request(next_url, callback=self.parse)
