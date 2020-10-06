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

class OmniControlsSpider(BaseSpider):
    name = 'omnicontrols.com'
    allowed_domains = ['omnicontrols.com']
    start_urls = ('http://www.omnicontrols.com/manufacturer_browse.aspx',)
    #start_urls = ('http://www.omnicontrols.com/SearchResult.aspx?categoryID=913',)

    def __init__(self, *args, **kwargs):
        super(OmniControlsSpider, self).__init__(*args, **kwargs)
        self.page_seen = defaultdict(dict)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        cats = []
        if response.url == self.start_urls[0]:
            cats += hxs.select('//table[@class="ContentTableBORDER"]//a[@class="ContentLINK"]/@href').extract()

        cats += hxs.select('//a[@class="ContentLINK" and starts-with(text(), "See all")]/@href').extract()

        for cat in cats:
            yield Request(urljoin_rfc(get_base_url(response), cat))

        pages = hxs.select('//table[@id="SearchTemplate13_DataGrid1"]'+
                           '//a[contains(@href, "SearchTemplate13$DataGrid1$_ctl1$")]')
        for page in pages:
            t = page.select('./text()').extract()
            if not t:
                continue

            t = t[0]
            if 'Next' in t or 'Previous' in t:
                continue

            page_num = re.search('(\d+)', t)
            if not page_num or page_num.groups()[0] not in self.page_seen[response.url]:
                if page_num:
                    self.page_seen[response.url][page_num.groups()[0]] = True
                yield FormRequest.from_response(response, formname='Form2',
                    formdata={'__EVENTTARGET': page.select('./@href').re('doPostBack\(\'(.*)\',')[0].replace('$', ':')},
                    dont_click=True)

        for product in self.parse_products(hxs, response):
            yield product

        print self.page_seen

    def parse_products(self, hxs, response):
        products = hxs.select('//table[contains(@id, "ProductInfoTable")]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', './/tr[contains(@id, "ProductNameRow")]//a/text()')
            url = product.select('.//tr[contains(@id, "ProductNameRow")]//a/@href').extract()
            if url:
                url = urljoin_rfc(get_base_url(response), url[0])
                loader.add_value('url', url)
            loader.add_xpath('price', './/tr[contains(@id, "RegularPrice")]//text()')
            yield loader.load_item()


