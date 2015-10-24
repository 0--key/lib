from scrapy.http import Request
from scrapy import log
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

import time, os
from urlparse import urljoin
from MTGPriceScraper.items import MtgpricescraperItem 

class TestSpider(BaseSpider):
    name = 'testspider'
    #allowed_domains = ['http://www.blackborder.com/', ]
    start_urls = ["http://www.blackborder.com/cgi-bin/prices/index.cgi", ]
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        magic_sets_full = hxs.select('//div[@class="left_block"]//ul[@class="left_menu"]//li/a/text()').extract()
        links_to_magic_sets_full = hxs.select('//div[@class="left_block"]//ul[@class="left_menu"]//li/a/@href').extract()
        # lets cut first category for debuging purposes:
        magic_sets = magic_sets_full[0]
        links_to_magic_sets = links_to_magic_sets_full[0]
        #self.log("This is first category and link to they: %s, %s, %s" % (type(magic_sets), magic_sets, links_to_magic_sets))
        # Now all magic sets are all together with the links to them:
        # uncoment this after debug:
        #magic_sets_zip = dict(zip(magic_sets, links_to_magic_sets))
        magic_sets_zip = dict([[magic_sets, links_to_magic_sets], ])
        date_prefix = time.strftime("%Y%m%d", time.localtime())
        try:
            os.mkdir("./archive/HTML/" + date_prefix)
        except OSError:
            self.log("The folder exists!")
        filename = "./archive/HTML/" + date_prefix + "/" + response.url.split("/")[-1] + ".htm"
        self.log("This is filename for index: %s" % (filename,))
        try:
            open(filename, 'wb').write(response.body)
        except OSError:
            os.remove(filename)
            open(filename, 'wb').write(response.body)
        # Continue to extract data:
        for magic_set, url in magic_sets_zip.iteritems():
            abs_url =  urljoin("http://www.blackborder.com", url)
            self.log("This is magic set name and url to it: %s ---> %s" % (magic_set, abs_url))
            request = Request(abs_url, callback=self.parse_set_page)
            request.meta['magic_set'] = magic_set
            request.meta['date_prefix'] = date_prefix
            yield request
    def parse_set_page(self, response):
        magic_set = response.request.meta['magic_set']
        date_prefix = response.request.meta['date_prefix']
        self.log("This is trailing magic set: %s" % (magic_set,))
        category = response.url.split("&")[-2]
        filename = "./archive/HTML/" + date_prefix + "/" + category.split("?")[-1] + ".htm"
        try:
            open(filename, 'wb').write(response.body)
        except OSError:
            os.remove(filename)
            open(filename, 'wb').write(response.body)
        hxs = HtmlXPathSelector(response)
        self.log("It is category catalog parser!")
        # now we at 'Top 20' page & can extract pagination if it exists!:
        links_to_pages = hxs.select('//table[@width="94%"]//tr//td[@align="center"]//table//tr/td//a/@href').extract()
        for links in links_to_pages:
            abs_url =  urljoin("http://www.blackborder.com/cgi-bin/prices/", links)
            self.log("This is abs urls to related pages: %s" % (abs_url,))
            request = Request(abs_url, callback=self.parse_catalog_page)
            request.meta['magic_set'] = magic_set
            request.meta['page_allocation'] = links.split("page=")[-1]
            request.meta['date_prefix'] = date_prefix
            yield request
    def parse_catalog_page(self, response):
        #self.log("This is catalogue page parser: %s" % (response.url,))
        magic_set = response.request.meta['magic_set']
        page_number = response.request.meta['page_allocation']
        date_prefix = response.request.meta['date_prefix']
        page_id = response.url.split("&")[-2:]
        filename = "./archive/HTML/" + date_prefix + "/" + page_id[0] + page_id[1] + ".htm"
        try:
            open(filename, 'wb').write(response.body)
        except OSError:
            os.remove(filename)
            open(filename, 'wb').write(response.body)
        hxs = HtmlXPathSelector(response)
        cards = hxs.select('//table[@class="table"]//td[@class="pgcol0"]/strong/a//text()').extract()
        links_to_buy_cards = hxs.select('//table[@class="table"]//td[@class="pgcol0"]/strong/a//@href').extract()
        low_price = hxs.select('//table[@class="table"]//td[@align="right"][@class="pgcol1"][1]/text()').extract()
        avg_price = hxs.select('//table[@class="table"]//td[@align="right"][@class="pgcol0"]/text()').extract()
        high_price = hxs.select('//table[@class="table"]//td[@class="pgcol1"][2]/text()').extract()
        # 3 stores, prices and links to them on each card!!
        stores_names = hxs.select('//table[@class="table"]//td[@class="pgcol0"][3]/a/text()').extract()
        links_to_stores = hxs.select('//table[@class="table"]//td[@class="pgcol0"][3]/a/@href').extract()
        price_in_stores = hxs.select('//table[@class="table"]//td[@class="pgcol0"][3]/strong/text()').extract()
        # let's zip it together and split into chunks:
        stores_info_zip = tuple(zip(stores_names, links_to_stores, price_in_stores))
        our_store_price = hxs.select('//table[@class="table"]//td[@align="center"][@class="pgcol1"]//strong/text()').extract()
        # items have trailing \n and we need delete it later!
        items_in_our_store = hxs.select('//table[@class="table"]//td[@align="center"][@class="pgcol1"]//option[last()]/text()').extract()
        cards_info_zip = tuple(zip(cards, links_to_buy_cards, low_price, avg_price, high_price, our_store_price, items_in_our_store))
        i=0
        items = []
        for card, link, low_price, avg_price, high_price, our_store_price, items_in_our_store in cards_info_zip:
            #let's iterate store info:
            stores_info = stores_info_zip[i:i+3]
            i=i+3
            for stores in stores_info:
                item = MtgpricescraperItem()
                item['card_name'] = card
                item['magic_set'] = magic_set
                item['page'] = page_number
                item['link'] = "http://www.blackborder.com" + link.split("&sid")[0]
                item['low_price'] = low_price.split("$")[-1]
                item['avg_price'] = avg_price.split("$")[-1]
                item['high_price'] = high_price.split("$")[-1]
                item['store_name'] = stores[0]
                item['link_to_store'] = "http://www.blackborder.com" + stores[1]
                item['price_in_store'] = stores[2].split("$")[-1]
                # let's implement transformation into decimal:
                if "$" in our_store_price:
                    item['our_store_price'] = our_store_price.split("$")[-1]
                else:
                    item['our_store_price'] = "0." + our_store_price
                item['items_in_our_store'] = items_in_our_store.split("\n")[0]
                items.append(item)
            return items
