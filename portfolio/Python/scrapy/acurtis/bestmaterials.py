import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

try:
    import json
except ImportError:
    import simplejson as json

import logging

js_api_request_args = {
    '__EVENTTARGET': '',
    '__EVENTARGUMENT': '',
    '__VIEWSTATE': '',
    'myhiddenfield': 'null',
    'variation_id': '',
    'w': 'getProductAttributeDetails'
}


class BestmaterialsSpider(BaseSpider):
    name = "bestmaterials"
    allowed_domains = ["bestmaterials.com"]
    start_urls = (
        'http://www.bestmaterials.com/',
        )
    manufacturers_urls = (
        'http://www.bestmaterials.com/SearchResult.aspx?Manufacturer=14',
        'http://www.bestmaterials.com/SearchResult.aspx?Manufacturer=54',
        'http://www.bestmaterials.com/SearchResult.aspx?Manufacturer=115',
        'http://www.bestmaterials.com/SearchResult.aspx?Manufacturer=104',
        )
    cat_1_url = 'http://www.bestmaterials.com/retrofit_pipe_flashing_boots.aspx'
    cat_2_url = 'http://www.bestmaterials.com/masterflash_sizes_and_materials.aspx'
    products_urls = (
        'http://www.bestmaterials.com/detail.aspx?ID=17345',
        'http://www.bestmaterials.com/detail.aspx?ID=17347',
        'http://www.bestmaterials.com/detail.aspx?ID=17348',
        'http://www.bestmaterials.com/detail.aspx?ID=17349',
        'http://www.bestmaterials.com/detail.aspx?ID=17271',
        'http://www.bestmaterials.com/detail.aspx?ID=17272',
        'http://www.bestmaterials.com/detail.aspx?ID=17273',
        'http://www.bestmaterials.com/detail.aspx?ID=17274',
        'http://www.bestmaterials.com/detail.aspx?ID=17275',
        )

    def parse(self, response):
        yield Request(self.cat_1_url, callback=self.parse_1_cat)
        yield Request(self.cat_2_url, callback=self.parse_2_cat)

        for url in self.manufacturers_urls:
            yield Request(url, callback=self.parse_manufacturer)

        for url in self.products_urls:
            yield Request(url, callback=self.parse_item)

    def parse_1_cat(self, response):
        hxs = HtmlXPathSelector(response)
        content = hxs.select("//td[@id='ContentCell']/table/tr/td")
        items = content.select("div[@align='center']/center/table[@id='AutoNumber1']/*/tr/td[1]")
        items = items.select(".//a/@href").extract()
        for item in items:
            yield Request(item, callback=self.parse_item)

        items = content.select("div[@align='center']/center/table[@id='AutoNumber2']/tr/td[1]")
        items = items.select(".//a/@href").extract()
        for item in items:
            yield Request(item, callback=self.parse_item)

    def parse_2_cat(self, response):
        hxs = HtmlXPathSelector(response)
        content = hxs.select("//td[@id='ContentCell']/table/tr/td")
        items = content.select("div[@align='center']/center/table[@id='AutoNumber1']/tr/td[1]")
        items = items.select(".//a/@href").extract()
        for item in items:
            yield Request(item, callback=self.parse_item)
        items = content.select("div[@align='center']/center/table[@id='AutoNumber2']/tr/td[1]")
        items = items.select(".//a/@href").extract()
        for item in items:
            yield Request(item, callback=self.parse_item)

    def parse_manufacturer_pages(self, response):
        hxs = HtmlXPathSelector(response)
        content = hxs.select("//td[@id='ContentCell']/table/tr/td[@class='Content']")
        items = content.select("div[@align='right']/div/table[2]")
        pages = items.select("tr[@class='Content']/td/a/@href").extract()
        for page in pages:
            "javascript:__doPostBack('SearchTemplate13$DataGrid1$_ctl1$_ctl1','')"
            m = re.search("doPostBack\('(.*?)','(.*?)'\)", page)
            if m:
                target = m.group(1)
                target = target.replace('$', ':')
                argument = m.group(2)

                item_options = js_api_request_args.copy()
                item_options['__VIEWSTATE'] = hxs.select("//form[@name='Form2']/input[@name='__VIEWSTATE']/@value").extract()
                item_options['__EVENTTARGET'] = target
                item_options['__EVENTARGUMENT'] = argument

                request = FormRequest(
                    url=response.url,
                    formdata=item_options,
                    callback=self.parse_manufacturer
                )
                yield request

        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        content = hxs.select("//td[@id='ContentCell']/table/tr/td[@class='Content']")
        items = content.select("div[@align='right']/div/table[2]")
        items = items.select("tr/td/table//td[@class='Content']/table/tr[2]/td/a/@href").extract()
        for item in items:
            yield Request(urljoin_rfc(base_url, item), callback=self.parse_item)

    def parse_manufacturer(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        content = hxs.select("//td[@id='ContentCell']/table/tr/td[@class='Content']")
        items = content.select("div[@align='right']/div/table[2]")
        items = items.select("tr/td/table//td[@class='Content']/table/tr[2]/td/a/@href").extract()
        for item in items:
            yield Request(urljoin_rfc(base_url, item), callback=self.parse_item)

    def parse_item(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        name = hxs.select("//tr[@id='ProductDetail11_trProductName']/td/text()").extract()
        if name:
            name = name[0].strip()
            url = response.url
            price = hxs.select("//tr[@id='ProductDetail11_trCustomPrice']/td/font/b/text()").extract()
            if not price:
                price = hxs.select("//tr[@id='ProductDetail11_trPrice']/td/text()").extract()

            l = ProductLoader(item=Product(), response=response)
            l.add_value('identifier', str(name))
            l.add_value('name', name)
            l.add_value('url', url)
            l.add_value('price', price)
            yield l.load_item()
        else:
            # may be several products
            products = hxs.select("//table[@id='SearchTemplate13_DataGrid1']// \
                                     table[@id='SearchTemplate13_DataGrid1__ctl3_ProductInfoTable']")
            for product in products:
                url = product.select("//tr[@id='SearchTemplate13_DataGrid1__ctl3_ProductNameRow']/td/a/@href").extract()
                if url:
                    yield Request(urljoin_rfc(base_url, url[0]), callback=self.parse_item)
