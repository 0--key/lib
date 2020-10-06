import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product
from scrapy.http import FormRequest

class DV247(BaseSpider):
    name = 'dv247.com'
    allowed_domains = ['dv247.com', 'www.dv247.com']
    start_urls = ('http://www.dv247.com',)

    def parse_product(self, response):
        URL_BASE = 'http://www.dv247.com'

        hxs = HtmlXPathSelector(response)
        
        products = hxs.select('//div[@class="listItem clearfix"]')
        for p in products:
            res = {}
            name = ' '.join(p.select('.//a//text()').extract())
            url = p.select('.//a/@href')[0].extract()
            url = urljoin_rfc(URL_BASE, url)
            price = p.select('.//li[@class="price"]/text()').re('\xa3(.*)')[0]
            res['url'] = url
            res['description'] = name
            res['price'] = price
            yield load_product(res, response)


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        URL_BASE = 'http://www.dv247.com'
        #categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//nav[@id="megamenu"]/ul/li/a/@href | \
                                    //nav[@id="megamenu"]//li[@class="accessories threeCol"]//a/@href').extract()
        #the following category had to be added manually because the link is broken.
        category_urls.append('/computer-music-software/')
        for url in category_urls:
            if url == '#':
                continue
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        #next page
        next_pages = hxs.select('//div[@class="listPaging"]')
        if next_pages:
            next_pages = next_pages[0].select('.//a[not(@class="selectedpage")]/@href').extract()
            for page in next_pages:
                url = urljoin_rfc(URL_BASE, page)
                yield Request(url)

        # products
        for p in self.parse_product(response):
            yield p
