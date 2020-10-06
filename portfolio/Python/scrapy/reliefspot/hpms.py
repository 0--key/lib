# scrapy includes
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

# spider includes
from product_spiders.items import Product, ProductLoader

# main class
class HPMSSpider(BaseSpider):

    # setup
    name = "hpms.com" # Name must match the domain
    allowed_domains = ["hpms.com"]
    start_urls = ["http://www.hpms.com/pindex.asp",]

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

        # detect multiple product page
        tableHeader = hxs.select("//td[text()='Item#']")

        if tableHeader:
            subProducts = tableHeader.select("../../tr[@class='Multi-Child_Background']")
            for subProduct in subProducts:
                loader = ProductLoader(Product(), subProduct)
                theTDs = subProduct.select("td")
                loader.add_value('sku', theTDs[0].select("text()").extract())
                loader.add_value('name', theTDs[1].select("text()").extract())
                loader.add_value('price', theTDs.select("b/text()").extract())
                loader.add_value('url', response.url)

                yield loader.load_item()

        else:
            productNode = hxs.select('//table[@id="v65-product-parent"]')[0]
            priceNode = productNode.select(".//font[@class='pricecolor colors_productprice']/text()")

            # Unavailable products are still online but have no price
            if priceNode:
                loader = ProductLoader(selector=productNode, item=Product())
                loader.add_xpath('name', './/font[@class="productnamecolorLARGE colors_productname"]/text()')
                loader.add_value('url', response.url)
                loader.add_value('price', priceNode.extract())
                sku = ''.join(hxs.select('.//span[@class="product_code"]/text()').extract()).strip()
                loader.add_value('sku', sku)

                yield loader.load_item()
