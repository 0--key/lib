import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest

class summerlandstackle_spider(BaseSpider):
    name = 'summerlands-tackle.co.uk'
    allowed_domains = ['summerlands-tackle.co.uk', 'www.summerlands-tackle.co.uk']
    start_urls = ('http://www.summerlands-tackle.co.uk/search.php',)

    def parse_product(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="product-single"]')
        for p in products:
            res = {}
            name = p.select('./form/div/div[@class="section-product-title"]/a/text()').extract()
            if name:
                url = p.select('./form/div/div[@class="section-product-title"]/a/@href')[0].extract()
                price = "".join(p.select('./form/div/div/span[@class="price"]/text()').re(r'([0-9\,\. ]+)')).strip()

                res['url'] = urljoin_rfc(base_url,url)
                res['description'] = name[0]
                res['price'] = price
                yield load_product(res, response)


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        base_url = get_base_url(response)
        
        #pages
        hxs = HtmlXPathSelector(response)
        pages_urls = hxs.select('//ul[@class="pages-list"]/li/a/@href').extract()
        for page in pages_urls:
            yield Request(page)
            
        # products
        for p in self.parse_product(response):
            yield p