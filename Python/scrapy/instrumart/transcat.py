import re
import json
from collections import defaultdict

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from product_spiders.utils import extract_price

class TranscatSpider(BaseSpider):
    name = 'transcat.com'
    allowed_domains = ['transcat.com']
    start_urls = ('http://www.transcat.com/Catalog/default.aspx',)
    start_urls = ('http://www.transcat.com/Catalog/ProductSearch.aspx?SearchType=Combo&Mfg=&Cat=CL&SubCat=',)

    def __init__(self, *args, **kwargs):
        super(TranscatSpider, self).__init__(*args, **kwargs)
        self.page_seen = defaultdict(dict)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        if response.url == self.start_urls[0]:
            cats = hxs.select('//td[@class="catalog-list"]/strong/a/@href').extract()
            for cat in cats:
                yield Request(urljoin_rfc(get_base_url(response), cat))

        pages = set(hxs.select('//tr[@class="Numbering"]//a/@href').re('_doPostBack\(.*,.*(Page\$\d+).*\)'))
        for page in pages:
            if not page in self.page_seen[response.url]:
                self.page_seen[response.url][page] = True
                r = FormRequest.from_response(response, formname='aspnetForm',
                    formdata={'__EVENTTARGET': 'ctl00$ContentPlaceHolderMiddle$TabContainer1$TabPanel2$grdSearch',
                              '__EVENTARGUMENT': page}, dont_click=True)
                yield r

        for product in self.parse_products(hxs, response):
            yield product

    def parse_products(self, hxs, response):
        products = hxs.select('//table[@class="SearchGrid"]//td/a[contains(@href, "productdetail.aspx")]/../..')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            url = product.select('.//a[contains(@href, "productdetail.aspx")]/@href').extract()[0]
            url = urljoin_rfc(get_base_url(response), url)
            loader.add_value('url', url)
            loader.add_xpath('name', './/td[position() = 2]//a[contains(@href, "productdetail.aspx")]/text()')
            loader.add_xpath('price', './/td[position() = 3]//text()')
            yield loader.load_item()

