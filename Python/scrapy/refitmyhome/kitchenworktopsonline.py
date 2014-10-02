from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

import re

from product_spiders.items import ProductLoader, Product

class kitchenworktopsonlineSpider(BaseSpider):

    name = "kitchenworktopsonline.co.uk"
    allowed_domains = ["kitchenworktopsonline.co.uk"]
    start_urls = ['http://www.kitchenworktopsonline.co.uk/sitemap.htm',]

    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        items = hxs.select("//a/@href").extract()
        for item in items:
            yield Request(urljoin_rfc(base_url,item), callback=self.parse_items)

    def parse_items(self,response):
        hxs = HtmlXPathSelector(response)
        options = hxs.select("//div[@id='primaList']").extract()
        if options:
            url = response.url
            lines = options[0].split("\n")
            title = ""
            for line in lines:
                price = None
                name = None
                h2 = re.search('a>(.*)</h2>', line)
                if h2: title = h2.group(1)
                val = re.search('name="price" value="([^"]*)"', line)
                if val: price = val.group(1)
                val = re.search('name="title" value="([^"]*)"', line)
                if val: name = val.group(1) + " " + title
                if price and name:
                    l = ProductLoader(item=Product(), response=response)
                    l.add_value('name', name.strip())
                    l.add_value('url', url)
                    l.add_value('price', price)
                    yield l.load_item()
