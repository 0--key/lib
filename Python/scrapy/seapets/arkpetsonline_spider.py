import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest

class siapets_spider(BaseSpider):
    name = 'arkpetsonline.co.uk'
    allowed_domains = ['arkpetsonline.co.uk', 'www.arkpetsonline.co.uk']
    start_urls = ('http://www.arkpetsonline.co.uk/aquariums-aquarium-supplies-c-2.html?currency=GBP',
                  'http://www.arkpetsonline.co.uk/pond-products-c-12.html?currency=GBP',
                  'http://www.arkpetsonline.co.uk/sale-items-c-901.html?currency=GBP',
                  'http://www.arkpetsonline.co.uk/reptile-products-c-44.html?currency=GBP',
                  'http://www.arkpetsonline.co.uk/dog-products-c-45.html?currency=GBP',
                  'http://www.arkpetsonline.co.uk/cat-products-c-46.html?currency=GBP',
                  'http://www.arkpetsonline.co.uk/bird-products-c-47.html?currency=GBP',
                  'http://www.arkpetsonline.co.uk/wild-bird-products-c-48.html?currency=GBP',
                  'http://www.arkpetsonline.co.uk/small-animal-products-c-49.html?currency=GBP',)
              
    def parse_product(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@id="indexProductList"]/div[@id="productListing"]/div/div[@class="item"]')
        for p in products:
            res = {}
            name = p.select('.//div[@class="item_name"]/a/text()')[0].extract()
            if name:
                url = p.select('.//div[@class="item_name"]/a/@href')[0].extract()
                price = p.select('.//div[@class="item_price"]/span[@class="productSpecialPrice"]/text()').re(r'([0-9][0-9\,\. ]+)')
                if not price:
                    price = p.select('.//div[@class="item_price"]/span[@class="price"]/text()').re(r'([0-9][0-9\,\. ]+)')
                res['url'] = urljoin_rfc(base_url,url)
                res['description'] = name
                res['price'] = price[0]
                yield load_product(res, response)


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        base_url = get_base_url(response)
        
        #categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//div[@class="categoryListBoxContents"]/a[@class="category_row"]/@href').extract()
        for url in category_urls:
            yield Request(url)
            
        #pages
        pages_urls = hxs.select('//div[@class="listing_links"]/a[@class="listing_number"]/@href').extract()
        for page in pages_urls:
            yield Request(page)


        # products
        for p in self.parse_product(response):
            yield p
