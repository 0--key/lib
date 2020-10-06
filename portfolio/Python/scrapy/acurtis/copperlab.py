from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.spider import BaseSpider

from product_spiders.items import Product, ProductLoader


class CopperlabSpider(BaseSpider):
    name = "copperlab"
    allowed_domains = ["copperlab.com"]
    start_urls = (
        'http://www.copperlab.com/store/drains.html?SID=2e09d69bd00371e0dc7ef78495e49645',
        )
    start_items = (
        'http://www.copperlab.com/store/fittings-accessories/clamping-ring.html',
        'http://www.copperlab.com/store/fittings-accessories/rubber-coupling.html',
        'http://www.copperlab.com/store/fittings-accessories/rubber-coupling-elbow.html',
        'http://www.copperlab.com/store/fittings-accessories/dome-strainer.html',
        'http://www.copperlab.com/store/fittings-accessories/parapet-dome-strainer.html',
        )

    def parse(self, response):
        for item in self.start_items:
            yield Request(item, callback=self.parse_item)

        hxs = HtmlXPathSelector(response)

        content = hxs.select("//div[@class='category-products']")

        pages = content.select("div[@class='toolbar']/div[@class='pager']/\
                                div[@class='pages']//a/@href").extract()
        for page in pages:
            yield Request(page, callback=self.parse)

        items = content.select("ul[@class='products-grid']/li/\
                                h2[@class='product-name']/a/@href").extract()
        for item in items:
            yield Request(item, callback=self.parse_item)

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)

        content = hxs.select("//div[@class='product-essential']//div[@class='product-shop']")

        name = content.select("div[@class='product-name']/h1/text()").extract()[0]
        url = response.url
        description = content.select("div[@class='short-description']/div").extract()[0]
        price = content.select("div[@class='price-box']//span[@class='price']/text()").extract()[0]

        l = ProductLoader(item=Product(), response=response)
        l.add_value('identifier', str(name))
        l.add_value('name', name)
        l.add_value('url', url)
        l.add_value('price', price)
        yield l.load_item()
