from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from product_spiders.items import ProductLoader, Product

import re

class refithomeSpider(BaseSpider):

    name = "refitmyhome.com"
    allowed_domains = ["refitmyhome.com"]
    start_urls = ['http://refitmyhome.com/',]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        content = hxs.select("//li[@class='catLevel3']")
        items = content.select(".//a/@href").extract()
        items.append(self.start_urls[0] + "Sale-Items/")
        for item in items:
            yield Request(item, callback=self.parse_items)


    def parse_items(self,response):
        hxs = HtmlXPathSelector(response)
        cats = hxs.select("//td[@class='subcategory']/a/@href").extract()
        if cats:
            for cat in cats:
                yield Request(cat, callback=self.parse_items)
        else:
            items = hxs.select("//td[@class='product-cell']")
            if items:
                for item in items:
                    product_url = item.select('.//a[@class="product-title"]/@href').extract()[0]
                    yield Request(product_url, callback=self.parse_item)

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)

        name = hxs.select("//div[@class='details']//h1/text()").extract()[0]
        url = response.url
        price = hxs.select("//div[@class='details']//span[@id='product_price']/text()").extract()[0]

        options = hxs.select("//td[@class='property-value']//select[starts-with(@name, 'product_options')]/option/text()").extract()
        if options:
            for opt in options:
                parts = opt.partition('(')
                opt_name = name + " - " + parts[0].strip()
                opt_price = price
                if parts[2]:
                    sign = parts[2][0]
                    if sign in ['-','+']:
                        addon = re.sub('[^0-9\.]','',parts[2])
                        if sign == '-':
                            opt_price = str(float(price) - float(addon))
                        else:
                            opt_price = str(float(price) + float(addon))
                l = ProductLoader(item=Product(), response=response)
                l.add_value('name', opt_name)
                l.add_value('url', url)
                l.add_value('price', opt_price)
                yield l.load_item()
        else:
            l = ProductLoader(item=Product(), response=response)
            l.add_value('name', name)
            l.add_value('url', url)
            l.add_value('price', price)
            yield l.load_item()
