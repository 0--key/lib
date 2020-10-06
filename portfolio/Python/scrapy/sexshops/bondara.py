import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from productloader import load_product

from scrapy.http import FormRequest

class Bondara(BaseSpider):
    name = 'bondara.co.uk'
    allowed_domains = ['bondara.co.uk', 'www.bondara.co.uk']
    start_urls = ('http://www.bondara.co.uk',)
    
    def __init__(self, *args, **kwargs):
        super(Bondara, self).__init__(*args, **kwargs)
        self.URL_BASE = 'http://www.bondara.co.uk'
        self.cookies = {}
        
    def start_requests(self):
        yield Request('http://www.bondara.co.uk', callback=self.set_cookies)
	
    def set_cookies(self, response):
        hxs = HtmlXPathSelector(response)
        script = hxs.select('//script/text()')[0].extract()
        res = re.findall('setCookie\(\\\'(.*?)\\\', \'(.*?)\'', script)
        self.cookies = {}
        if res:
            self.cookies[res[0][0]] = res[0][1]
            self.cookies['DOAReferrer'] = 'http://www.bondara.co.uk/'
        yield Request(response.url, cookies=self.cookies, callback=self.parse,
		          dont_filter = True)
        
    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        products = hxs.select('//div[@class="wideboxprodlist"]')
        for product in products:
            res = {}
            try:
                name = product.select('.//a/@title').extract()[0]
                url = product.select('.//a/@href').extract()[0]
                url = urljoin_rfc(self.URL_BASE, url)
                price = product.select('.//div[@class="price"]/span[contains(@id,"price")]/text()').re('\xa3(.*)')[0]
                res['url'] = url
                res['description'] = name
                res['price'] = price
                res['sku'] = ''
                yield load_product(res, response)
            except IndexError:
                return


    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)
        # categories
        categories = hxs.select('//div[@id="tabmenu"]//a[@class="MenuBarItemSubmenu"]/@href').extract()
        for url in categories:
            url = urljoin_rfc(self.URL_BASE, url)
            yield Request(url, cookies=self.cookies)

        # next page
        next_page = hxs.select('//div[@class="paginate_product_finder_pages"]//a[contains(text(), "Next")]/@href').extract()
        if next_page:
            next_page = urljoin_rfc(self.URL_BASE, next_page[0])
            yield Request(next_page, cookies=self.cookies)

        # products
        for product in self.parse_product(response):
            yield product
