from urlparse import urljoin
from scrapy import log

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request

from sydney.items import SupplierItem

###############################################################################


class SupplierSpider(Spider):
    name = 'banana'
    start_urls = [
        'http://www.sydneymarkets.com.au/produce-suppliers.asp?foo=bar&page=1',
        'http://www.sydneymarkets.com.au/produce-suppliers.asp?foo=bar&page=2',
        'http://www.sydneymarkets.com.au/produce-suppliers.asp?foo=bar&page=3',
        'http://www.sydneymarkets.com.au/produce-suppliers.asp?foo=bar&page=4',
        'http://www.sydneymarkets.com.au/produce-suppliers.asp?foo=bar&page=5',
        'http://www.sydneymarkets.com.au/produce-suppliers.asp?foo=bar&page=6',
        ]

    def parse(self, response):
        sel = Selector(response)
        raw_links = sel.xpath(
            '//table[@class="marketdirectory"]//tr/td[@width="30%"]/a/@href'
            ).extract()
        for i in raw_links:
            sup_page_url = urljoin('http://www.sydneymarkets.com.au', i)
            req = Request(url=sup_page_url, callback=self.parse_supplier)
            yield req

    def parse_supplier(self, response):
        sel = Selector(response)
        log.msg("This is a warning from %s" % response.url, level=log.WARNING)
        item = SupplierItem()
        item['trading_name'] = sel.xpath(
            '//table[@class="descriptionbox"]//tr[2]/td/strong/text()'
            ).extract()
        item['stall_location'] = sel.xpath(
            '//table[@class="descriptionbox"]//tr[3]/td/text()'
            ).extract()
        item['phone'] = sel.xpath(
            '//table[@class="descriptionbox"]//tr[4]/td/text()'
            ).extract()
        item['fax'] = sel.xpath(
            '//table[@class="descriptionbox"]//tr[5]/td/text()'
            ).extract()
        item['products_sold'] = ";".join(
            sel.xpath(
                '//table[@class="marketdirectory"]//tr/td/text()'
                ).extract())
        return item
