from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

try:
    import json
except ImportError:
    import simplejson as json


class FastenalSpider(BaseSpider):
    name = "fastenal"
    allowed_domains = ["fastenal.com"]
    start_urls = (
        'http://www.fastenal.com/web/search/product/fasteners/hardware/flashing-products/_/Navigation?searchterm=&sortby=&sortdir=&searchmode=&refine=~|categoryl1:%22600000%20Fasteners%22|~%20~|categoryl2:%22600206%20Hardware%22|~%20~|categoryl3:%22600213%20Flashing%20Products%22|~',
        )

    def parse(self, response):
        base_url = get_base_url(response)

        hxs = HtmlXPathSelector(response)

        pages = hxs.select("//div[@id='content']/div[@id='attribute-table']/\
                              div[@class='container']/table[@class='pagination']//\
                              a/@href").extract()
        for page in pages:
            yield Request(urljoin_rfc(base_url, page), callback=self.parse)

        items = hxs.select("//div[@id='content']/div[@id='attribute-table']/\
                              div[@class='container']/table[@id='searchResults']//\
                              tr/td[@class='description']/div/a/@href").extract()
        for item in items:
            yield Request(urljoin_rfc(base_url, item), callback=self.parse_item)

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)

        item = hxs.select("//div[@id='content']/div[@class='container']/\
                             div[@id='mainDetailsContainer']")
        title = item.select("h1/text()").extract()
        url = response.url
        price = item.select("div[@id='grayVerticalSeparator']/div[@id='buyingInformation']/\
                             p[@class='wholesale']/text()").extract()
        if not price:
            price = item.select("div[@id='grayVerticalSeparator']/div[@id='buyingInformation']/\
                                 p[@class='wholesale strike']/text()").extract()

        l = ProductLoader(item=Product(), response=response)
        l.add_value('identifier', str(title))
        l.add_value('name', title)
        l.add_value('url', url)
        l.add_value('price', price)
        return l.load_item()
