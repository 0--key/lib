from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class LystfiskerenDkSpider(BaseSpider):
    name = 'lystfiskeren.dk'
    allowed_domains = ['lystfiskeren.dk']
    start_urls = ('http://www.lystfiskeren.dk',)
    junk_urls = (
            # Shipping prices
            'http://www.lystfiskeren.dk/shop/fragttill%C3%A6g+-+shipping/?g=251',
            )

    def parse(self, response):
        if response.url in self.junk_urls:
            return

        hxs = HtmlXPathSelector(response)

        for item in hxs.select(u'//div[@class="item_wrapper"]'):
            product_loader = ProductLoader(item=Product(), selector=item)

            product_loader.add_xpath('name', u'.//div[@class="name"]/a/text()')

            price = item.select(u'.//div[@class="price"]/text()[last()]').extract()[0]
            price = price.strip().lstrip('Kr. ').replace('.', '').replace(',', '.')
            product_loader.add_value('price', price)

            url = item.select(u'.//div[@class="name"]/a/@href').extract()[0]
            url = urljoin_rfc(get_base_url(response), url)
            product_loader.add_value('url', url)

            yield product_loader.load_item()

        level = response.meta.get('level', 1)
        sub_url = u'//div[@id="shopnav"]/' + u'/'.join([u'ul/li'] * level) + '/a/@href'
        subcategories = hxs.select(sub_url).extract()
 
        for subcategory in subcategories:
            url = urljoin_rfc(get_base_url(response), subcategory)
            yield Request(url, meta={'level': level+1})
