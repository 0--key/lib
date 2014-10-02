from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.markup import replace_tags

from product_spiders.items import Product, ProductLoader


class PipebootexpressComSpider(BaseSpider):
    name = 'pipebootexpress.com'
    allowed_domains = ['pipebootexpress.com']
    start_urls = (
        'http://pipebootexpress.com/',
        )

    download_delay = 2

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        categories = hxs.select("//div[@id='dvWrapControl732']//a/@href").extract()
        for link in categories:
            url = urljoin_rfc(base_url, link)
            yield Request(url, callback=self.parse)

        items = hxs.select("//table[@class='ProductGroup']/tr[@class='ProductGroupItem'] |\
                            //table[@class='ProductGroup']/tr[@class='ProductGroupAlternatingItem']")
        for item in items:
            name = item.select("td[@id='tdProductGroupDisplayDescription']/div/font | \
                                td[@id='tdProductGroupDisplayAltDescription']/div/font").extract()
            if not name:
                print "%s - ERROR! NO NAME!" % response.url
                continue
            name = replace_tags(name[0])
            url = response.url
            price = item.select("td[@id='tdProductGroupDisplayPricing']//text() | \
                                 td[@id='tdProductGroupDisplayAltPricing']//text()").extract()
            if not price:
                print "%s - ERROR! NO PRICE!" % response.url
                continue
            price = price[0].split(',')[0]
            l = ProductLoader(item=Product(), response=response)
            l.add_value('identifier', unicode(name).encode('ascii', 'ignore'))
            l.add_value('name', name)
            l.add_value('url', url)
            l.add_value('price', price)
            yield l.load_item()
