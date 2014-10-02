import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

PROXY = 'http://ec2-107-20-62-101.compute-1.amazonaws.com:6543'

def proxyRequest(*args, **kwargs):
    meta = {'proxy': PROXY}
    if 'meta' in kwargs:
        kwargs['meta'].update(meta)
    else:
        kwargs['meta'] = meta
    return Request(*args, **kwargs)


class RoofingsupplyusaSpider(BaseSpider):
    name = "roofingsupplyusa"
    allowed_domains = ["roofingsupplyusa.com"]
    start_urls = (
        'http://www.roofingsupplyusa.com/Olympic-.html',
        'http://www.roofingsupplyusa.com/store/p/5761-Zurn-Z121-Deck-Plate.html',
        'http://www.roofingsupplyusa.com/J-R-Smith.html',
        'http://www.roofingsupplyusa.com/By-Manufacturer/Wade.html',
        'http://www.roofingsupplyusa.com/By-Manufacturer/Josam.html',
        )
    start_items = (
        'http://www.roofingsupplyusa.com/store/p/5322-Marathon-Plastic-Strainers.html',
        'http://www.roofingsupplyusa.com/store/p/4602-Marathon-Adjustable-Drain-Guards.html',
        )

    download_delay = 3

    def parse(self, response):
        base_url = get_base_url(response)

        for item in self.start_items:
            yield Request(item, callback=self.parse_item)

        hxs = HtmlXPathSelector(response)

        content = hxs.select("//div[@class='LayoutMiddleBody']")

        pages = content.select("div[@id='dvNavTop']/div[@class='CategoryPageNavigation']//a/@href").extract()
        for page in pages:
            yield Request(urljoin_rfc(base_url, page), callback=self.parse)

        items = content.select("table[@id='dlCategory']//div[@id='divProductRow']/\
                                div[@class='CategoryProductThumbnailArea']/\
                                a[@class='CategoryProductThumbnail']/@href").extract()
        for item in items:
            yield Request(urljoin_rfc(base_url, item), callback=self.parse_item)

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)

        content = hxs.select("//div[@class='LayoutMiddleBody']")

        name = content.select(
                "div[@class='ProductDetailsProductName']/\
                 h1[@class='ProductDetailsProductName']/text()").extract()[0]
        description = content.select(
                "div[@class='ProductDetailsTabs']/div[@id='tabs']").extract()
        if description:
            description = description[0]
        url = response.url

        options = content.select("div[@class='ProductDetailsVariations']/\
                                  select[@class='variantDropDown']/option")
        found_products = False
        if options:
            # adding products variations from options
            for option in options:
                text = option.select("text()").extract()[0]
                # item_id = option.select("@value").extract()[0]
                m = re.search("(.*?)[\s]*/[\s]*(.*?)$", text)
                if m:
                    name_part = m.group(1)
                    item_name = name + " " + name_part
                    price = m.group(2)
                    l = ProductLoader(item=Product(), response=response)
                    l.add_value('identifier', str(item_name))
                    l.add_value('name', item_name)
                    l.add_value('url', url)
                    l.add_value('price', price)
                    yield l.load_item()
                    found_products = True
        if not found_products:
            # adding one product
            price = content.select(
                    "div[@class='ProductDetailsPricing']/\
                     span[@class='ProductDetailsPriceArea']/\
                     span[@class='ProductDetailsPrice PriceToUpdate']/text()").extract()
            if price:
                price = price[0]
                l = ProductLoader(item=Product(), response=response)
                l.add_value('identifier', str(name))
                l.add_value('name', name)
                l.add_value('url', url)
                l.add_value('price', price)
                yield l.load_item()
