from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from product_spiders.items import ProductLoader, Product

class blingkitchenSpider(BaseSpider):

    name = "blingyourkitchen.co.uk"
    allowed_domains = ["blingyourkitchen.co.uk"]
    start_urls = ['http://www.blingyourkitchen.co.uk',]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        items = hxs.select("//div[@id='nav']//li/a/@href").extract()
        for item in items:
            yield Request(item, callback=self.parse_items)
        for i in range(1,166):
            yield Request(self.start_urls[0] + "/s.do?id=0&itemType=1&keywords=+&page=" + str(i), callback=self.parse_items)

    def parse_items(self,response):
        hxs = HtmlXPathSelector(response)
        cats = hxs.select("//table[@class='hi']//span[@class='category']/a/@href").extract()
        if cats:
            for cat in cats:
                yield Request(cat, callback=self.parse_items)
        else:
            items = hxs.select("//tr[@class='row0']")
            if items:
                for item in items:
                    l = ProductLoader(item=Product(), response=item)
                    name = item.select('.//span[@class="name"]/a/text()').extract()
                    url = item.select('.//span[@class="name"]/a/@href').extract()
                    price = item.select('.//span[@class="price_inc"]/text()').extract()
                    l.add_value('name', name)
                    l.add_value('url', url)
                    l.add_value('price', price)
                    yield l.load_item()
