import exceptions
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class AllWeathersSpider(BaseSpider):
    name = 'allweathers.co.uk'
    allowed_domains = ['allweathers.co.uk']
    start_urls = ['http://www.allweathers.co.uk']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        relative_urls = hxs.select('//*[@id="siteBrandsDrowpDownSelect"]/'
                                   'option[not(@value="")]/@value').extract()
        for relative_url in relative_urls:
                url = urljoin_rfc('http://www.allweathers.co.uk', relative_url)
                yield Request(url, callback=self.parse_categories, dont_filter=True)                

    def parse_categories(self, response):
        try:
            hxs = HtmlXPathSelector(response)
            sub_categories = hxs.select('//div[@class="category-row"]/div/div/'
                                        'div[@class="category-item-name"]/'
                                        'a/@href').extract()
            if not sub_categories:
                products = hxs.select('//div[@class="wood-product "]')
                for product in products:
                    loader = ProductLoader(item=Product(), selector=product)
                    loader.add_xpath('name', 'div/div/div/'
                                             'div[@class="wood-product-name"]/'
                                             'a/text()')
                    relative_url = product.select('div/div/div/'
                                                  'div[@class="wood-product-name"]/'
                                                  'a/@href').extract()[0]
                    url = urljoin_rfc('http://www.allweathers.co.uk', relative_url)
                    loader.add_value('url', url)
                    loader.add_xpath('price','div/div/div/'
                                             'div[@class="wood-product-price"]/'
                                             'text()')
                    yield loader.load_item()
            else:
                relative_urls =  hxs.select('//div[@class="category-row"]/div/'
                                            'div/div[@class="category-item-name"]/'
                                            'a/@href').extract()
                for relative_url in relative_urls:
                    url = urljoin_rfc('http://www.allweathers.co.uk', relative_url)
                    yield Request(url, callback=self.parse_categories, dont_filter=True)
        except exceptions.AttributeError:
             if 'ret' in response.meta:
                 if response.meta['ret']<=5: 
                     yield Request(response.url, callback=self.parse_categories,
                                   dont_filter=True, meta={'ret': response.meta['ret']+1})
             else:
                 yield Request(response.url, callback=self.parse_categories, 
                               dont_filter=True, meta={'ret': 1})
                
                    
