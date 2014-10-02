import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest

class ericsangling_spider(BaseSpider):
    name = 'ericsangling.co.uk'
    allowed_domains = ['ericsangling.co.uk', 'www.ericsangling.co.uk','www.britnett-carveradv.co.uk','britnett-carveradv.co.uk']
    start_urls = ('http://www.ericsangling.co.uk',)

    def parse_product(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//table[@class="prodtable"]/tr')
        for p in products:
            res = {}
            name = p.select('.//td[@class="prodtableitem"]/a/text()').extract()
            if name:
                url = p.select('.//td[@class="prodtableitem"]/a/@href')[0].extract()
                price = "".join(p.select('.//td[@class="prodtableprice"]/text()').re(r'([0-9\,\. ]+)')).strip()

                res['url'] = urljoin_rfc(base_url,url)
                res['description'] = name[0]
                res['price'] = price
                yield load_product(res, response)


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        base_url = get_base_url(response)
        
        #categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//div[@id="navCatContent828"]/a/@href').extract()
        for url in category_urls:
            yield Request(url)
            
        # products
        for p in self.parse_product(response):
            yield p