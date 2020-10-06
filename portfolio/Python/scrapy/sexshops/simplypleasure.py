import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product

from scrapy.http import FormRequest

class SimplyPleasure(BaseSpider):
    name = 'simplypleasure.co.uk'
    allowed_domains = ['simplypleasure.com', 'www.simplypleasure.com']
    start_urls = ('http://www.simplypleasure.com/sitemap.aspx',)
    
    def __init__(self, *args, **kwargs):
        super(SimplyPleasure, self).__init__(*args, **kwargs)
        self.URL_BASE = 'http://www.simplypleasure.com'
        
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        res = {}
        try:
            name = hxs.select('//div[@class="productInfo"]/h1/text()').extract()[0]
            url = response.url
            price = hxs.select('//span[@class="price last"]/text()').re('\xa3(.*)')
            if price:
                price = price[0]
            else:
                price = hxs.select('//span[@class="price"]/text()').re('\xa3(.*)')[0]
            #sku = hxs.select('//div[@class="productInfo"]/p/text()').re(': (.*)')[0]
            sku = hxs.select('//div[@class="productInfo"]/p/text()').re('Product code:\r\n(.*)')[0].strip()
            res['url'] = url
            res['description'] = name
            res['price'] = price
            res['sku'] = sku
            yield load_product(res, response)
        except IndexError:
            return


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)
        # categories
        categories = hxs.select('//div[@class="leftBox"]/div[@id="vNav"]//a/@href').extract()
        categories = [urljoin_rfc(self.URL_BASE, cat) for cat in categories]

        if categories:
            yield Request(categories[0], meta={'categories': categories[1:]}, callback=self.parse_category)

    def parse_category(self, response):
        # next page
        hxs = HtmlXPathSelector(response)

        next_page = hxs.select('//a[text()=">"]/@href').re('k\(\'(.*?)\'')
        if next_page:
            formname = 'aspNetForm'
            formdata = {'__EVENTTARGET': next_page, '__EVENTARGUMENT': ''}
            request = FormRequest.from_response(response, formname=formname,
                                                formdata=formdata,
                                                dont_click=True, callback=self.parse_category,
                                                meta={'categories': response.meta['categories'][:]})
            yield request
        elif response.meta['categories']:
            cat = response.meta['categories'][0]
            yield Request(cat, meta={'categories': response.meta['categories'][1:]},
                          callback=self.parse_category)

        # products
        products = hxs.select('//div[@id="content" and @class="content"]//h3/a/@href').extract()
        for product in products:
            product = urljoin_rfc(self.URL_BASE, product)
            yield Request(product, callback=self.parse_product)
