from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.http.cookies import CookieJar
from scrapy import log

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class KettnerSpider(BaseSpider):
    name = 'kettner.fr'
    allowed_domains = ['kettner.fr']
    start_urls = ('http://www.kettner.fr',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        categories = hxs.select('//div[@id="menu"]/a/@href').extract()
        for cat in categories:
            yield Request(cat, callback=self.parse_subcategories)

    def parse_subcategories(self, response):
        hxs = HtmlXPathSelector(response)

        subcats = hxs.select('//div[@class="menu_left"]//a/@href').extract()
        pages = hxs.select('//div[@class="top_pagination"]//a/@href').extract()
        subcats += pages
        for subcat in subcats:
            yield Request(urljoin_rfc(get_base_url(response), subcat), callback=self.parse_subcategories)

        products = hxs.select('//div[@id="product_list"]//div[@class="Ncaps"]//div[@class="name"]/a/@href').extract()
        for product in products:
            yield Request(product, callback=self.parse_product)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        
        loader = ProductLoader(item=Product(), response=response)
        loader.add_value('url', response.url)
        name = hxs.select('//h1/a/text()').extract()[0].strip()
        for sub_name in hxs.select('//div[@class="choice_list_area"]//option[@selected]/text()').extract():
            name += ' ' + sub_name.strip()
            
        loader.add_value('name', name)
        price = hxs.select('//span[@class="price"]/text()').extract()[0]
        price = price.replace(',', '.')
        loader.add_value('price', price)
        yield loader.load_item()
        
        option_lists = hxs.select('//div[@class="choice_list_area"]//select')
        for option_list in option_lists:
            url = option_list.select('./@onchange').extract()[0]
            url = url.split(',')[2].strip("'")
            options = option_list.select('./option[not(@selected)]/@value').extract()
            for option in options:
                yield Request(url + option, callback=self.parse_product)

