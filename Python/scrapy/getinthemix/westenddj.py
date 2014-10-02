import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest

class WestendDJ(BaseSpider):
    name = 'westenddj.co.uk'
    allowed_domains = ['westenddj.co.uk', 'www.westenddj.co.uk']
    start_urls = ('http://www.westenddj.co.uk',)

    def parse_product(self, response):

        hxs = HtmlXPathSelector(response)
        
        products = hxs.select('//div[@class="list-item"]')
        for p in products:
            res = {}
            name = p.select('./a[@class="headline"]/text()')[0].extract()
            url = p.select('./a[@class="headline"]/@href')[0].extract()
            price = p.select('./span[@class="price"]/text()').re('\xa3(.*)')[0]
            res['url'] = url
            res['description'] = name
            res['price'] = price
            yield load_product(res, response)


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        
        #categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//div[@id="nav-container"]/ul[@id="menu"]/li[@class="mega"]/a/@href').extract()
        for url in category_urls:
            yield Request(url)

        #next page
        next_page = hxs.select('//img[@class="next"]/../@href')
        if next_page:
            next_page = next_page[0].re('ProductPage\(\'1\',\'(.*)\'')
            form_name = 'ProductPageForm1'
            sort_order = hxs.select('//select[@name="SortOrder"]/option[@selected]/@value')[0].extract()
            rec = hxs.select('//select[@name="recNumber"]/option[@selected]/@value')[0].extract()
            form_data = {'rec': rec, 's': sort_order, 'pg': next_page }
            request = FormRequest.from_response(response, formname=form_name, formdata=form_data,
                                            dont_click=True)
            yield request

        # products
        for p in self.parse_product(response):
            yield p
