import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest

class BtpMat_spider(BaseSpider):
    name = 'btpmat.fr'
    allowed_domains = ['btpmat.fr', 'www.btpmat.fr']
    start_urls = ('http://www.btpmat.fr',)

    def parse_product(self, response):
        
        hxs = HtmlXPathSelector(response)

        products = hxs.select('//li[contains(@class,"hreview-aggregate hproduct")]')
        for p in products:
            res = {}
            name = p.select('.//div/div/span/a/text()')[0].extract()
            url = p.select('.//div/div/span/a/@href')[0].extract()
            price = p.select('.//div/div/div/span/small/text()').re(r'([0-9\.\, ]+)')[0]
            res['url'] = url
            res['description'] = name
            res['price'] = price
            yield load_product(res, response)


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
            
        #categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//ul[@id="mainleftmenu"]//li/a/@href').extract()
        for url in category_urls:
            yield Request(url)            
            
        #subcategories
        subcategory_urls = hxs.select('//div[@class="category-elt"]/p/a/@href').extract()
        for url in subcategory_urls:
            yield Request(url)
            
            
        #next page
        next_pages = hxs.select('//div[@class="pages"]/ol//li/a/@href').extract()
        if next_pages:
            for page in next_pages:
                yield Request(page)

        # products
        for p in self.parse_product(response):
            yield p
