import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest

class climaxtackle_spider(BaseSpider):
    name = 'climaxtackle.com'
    allowed_domains = ['climaxtackle.com', 'www.climaxtackle.com']
    start_urls = ('http://www.climaxtackle.com/mm5/merchant.mvc?Screen=SRCH&Store_Code=1&search=*&offset=0&filter_cat=&PowerSearch_Begin_Only=&sort=name.asc&range_low=&range_high=',)

    def parse_product(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//table/tr/td/table[@cellpadding="2"]/tr')
        for p in products:
            res = {}
            try:
                name = p.select('./td[3]/font/text()')[0].extract().strip()
            except:
                continue
            if name:
                url = p.select('./td[2]/font/a/@href')[0].extract().strip()
                price = "".join(p.select('./td[4]/font/text()').re(r'([0-9\,\. ]+)')).strip()

                res['url'] = url
                res['description'] = name
                res['price'] = price
                yield load_product(res, response)


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        base_url = get_base_url(response)
        
        #pages
        hxs = HtmlXPathSelector(response)
        pages_urls = hxs.select('//table/tr/td/table/tr/td[@align="right"]/font/a/@href').extract()
        for page in pages_urls:
            yield Request(page)
            
        # products
        for p in self.parse_product(response):
            yield p