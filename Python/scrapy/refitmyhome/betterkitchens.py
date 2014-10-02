from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

import re

from product_spiders.items import ProductLoader, Product

class betterkitchensSpider(BaseSpider):

    name = "betterkitchens.co.uk"
    allowed_domains = ["betterkitchens.co.uk"]
    start_urls = ['http://www.betterkitchens.co.uk/search.asp?search=%20',]

    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        items = hxs.select("//div[@id='HLooperContainer']//div[@align='left']/a/@href").extract()
        if items:
            for item in items:
                yield Request(urljoin_rfc(base_url,item.replace(' ', '%20')), callback=self.parse_items)
            yield Request(self.start_urls[0] + "&offset=0", callback=self.parse_items)

    def parse_items(self,response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        items = hxs.select("//table[@class='full_border']//span[@class='short_title']/a/@href").extract()
        if items:
            for item in items:
                yield Request(urljoin_rfc(base_url,item), callback=self.parse_item)

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)
        url = response.url
        options = hxs.select("//div[@id='ProductMainDetails']//table[@class='sku_border']//table[@class='sku_table_items']")
        if options:
            for opt in options:
                name = opt.select(".//td/span[@class='sku_items']/text()").extract()[1]
                price = opt.select(".//td[@class='sku_items']/text()").extract()[0]
                if float(re.sub('[^0-9\.]', '', price)) > 0.00:
                    l = ProductLoader(item=Product(), response=response)
                    l.add_value('name', name.strip())
                    l.add_value('url', url)
                    l.add_value('price', price)
                    yield l.load_item()
