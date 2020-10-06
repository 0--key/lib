# scrapy includes
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

# spider includes
from product_spiders.items import Product, ProductLoader

# main class
class ReliefSpotSpider(BaseSpider):

    # setup
    name = "reliefspot.com" # Name must match the domain
    allowed_domains = ["reliefspot.com"]
    start_urls = ["http://www.reliefspot.com/pindex.asp",]

    # main request
    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # extract table nodes and page urls
        masterTables = hxs.select("//td[starts-with(text(),'Page:')]/../../../table")
        pageurls = set(masterTables[0].select(".//a/@href").extract())

        # iterate page urls
        for pageurl in pageurls:
            yield Request(urljoin_rfc(base_url, pageurl))

        # extract products
        productUrls = masterTables[1].select(".//tr/td/a/@href").extract()
        for productUrl in productUrls:
            yield Request(productUrl, callback=self.parse_product)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)
        loader = ProductLoader(response=response, item=Product())
        loader.add_xpath('name', '//font[@class="productnamecolorLARGE colors_productname"]/text()')
        loader.add_value('url', response.url)
        loader.add_xpath('price', '//font[@class="pricecolor colors_productprice"]/text()')
        sku = (''.join(hxs.select('//span[@class="product_code"]/text()').extract()).strip())
        # sku = [x.strip() for x in sku if x.strip()]
        sku = sku[3:]
        loader.add_value('sku', sku)
        # loader.add_value('sku', "the_sku")

        yield loader.load_item()
