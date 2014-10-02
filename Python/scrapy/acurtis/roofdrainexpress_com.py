from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader


class RoofdrainexpressComSpider(BaseSpider):
    name = 'roofdrainexpress.com'
    allowed_domains = ['roofdrainexpress.com']
    start_urls = (
        'http://roofdrainexpress.com/',
        )

    download_delay = 2

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        categories = hxs.select("//div[@id='dvWrapControl774']//a/@href").extract()
        for link in categories:
            url = urljoin_rfc(base_url, link)
            yield Request(url, callback=self.parse)

        manufacturers = hxs.select("//div[@id='dvWrapControl956']//a/@href").extract()
        for link in manufacturers:
            url = urljoin_rfc(base_url, link)
            yield Request(url, callback=self.parse)

        pages = hxs.select("//div[@class='ProductListPaging']//a/@href").extract()
        for link in pages:
            url = urljoin_rfc(base_url, link)
            yield Request(url, callback=self.parse)

        items = hxs.select("//div[@id='divProductRow']/div/\
                              span[@class='CategoryProductNameLink']/a/@href").extract()
        for item in items:
            url = urljoin_rfc(base_url, item)
            yield Request(url, callback=self.parse_item)

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)

        body = hxs.select("//div[@class='LayoutMiddleBody']/table[1]")

        name = body.select(".//h1[@class='ProductDetailsProductName']/text()").extract()
        if not name:
            print "%s - ERROR! NO NAME!" % response.url
            return
        name = name[0]
        url = response.url
        prices_vars = body.select(".//select[@id='ProductVariations_variantGroup1']/option")
        if prices_vars:
            for option in prices_vars:
                price = option.select("text()").extract()
                if not price:
                    print "%s - ERROR! NO PRICE!" % response.url
                    continue
                sub_name = name + " " + price[0].split('/')[0]
                price = price[0].split('/')[-1]
                l = ProductLoader(item=Product(), response=response)
                l.add_value('identifier', str(sub_name))
                l.add_value('name', sub_name)
                l.add_value('url', url)
                l.add_value('price', price)
                yield l.load_item()
        else:
            price = body.select(".//span[@class='ProductDetailsPriceArea']/\
                                    span[@class='ProductDetailsPrice']/text()").extract()
            if not price:
                print "%s - ERROR! NO PRICE!" % response.url
                return
            price = price[0].split(',')[0]
            l = ProductLoader(item=Product(), response=response)
            l.add_value('identifier', str(name))
            l.add_value('name', name)
            l.add_value('url', url)
            l.add_value('price', price)
            yield l.load_item()
