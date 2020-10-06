from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

import re

from product_spiders.items import ProductLoader, Product

class worktopsukSpider(BaseSpider):

    name = "www.worktops.uk.com"
    allowed_domains = ["www.worktops.uk.com"]
    start_urls = ['http://www.worktops.uk.com/',]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        items = hxs.select("//div[@id='category_tree_container']//li/a/@href").extract()
        for item in items:
            yield Request(item, callback=self.parse_items)

    def parse_items(self,response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        items = hxs.select("//div[@id='product_list']//tr[@class='product_thumbnail product']")
        if items:
            for item in items:
                no_price = item.select(".//span[@class='no_price']")
                if not no_price:
                    product_url = item.select(".//td[@class='name']//a/@href").extract()
                    if product_url:
                        yield Request(urljoin_rfc(base_url, product_url[0]), callback=self.parse_item)
        is_page = re.match(r'(.*)page=\d(.*)', response.url)
        if not is_page:
            pages = hxs.select("//div[@class='footer']//span[@class='pager']//strong/text()").extract()
            if pages:
                total = int(pages[0].strip())
                for p in range(2,total+1):
                    yield Request(response.url + "?page=" + str(p), callback=self.parse_items)
            cats = hxs.select("//div[@class='sub_categories']//div[@class='focus_category']//h5/a/@href").extract()
            if cats:
                for cat in cats:
                    yield Request(cat, callback=self.parse_items)

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)
        url = response.url
        name = hxs.select("//h1[@class='name']//span/text()").extract()[0]
        price = hxs.select("//div[@id='product_price']/text()").extract()[0]
        if price: price = re.sub('[^0-9\.]', '', price)
        if (price == '999.99'): price = ""
        if price and price != "":
         selects = hxs.select("//select[starts-with(@name, 'selected_options')]")
         if selects:
            total = len(selects)
            i = 0
            for txt in selects:
                i += 1
                options = txt.select(".//option/text()").extract()
                if options:
                    for opt in options:
                        parts = opt.partition('(')
                        opt_name = name + " - " + parts[0].strip()
                        opt_price = price
                        if parts[2]:
                            sign = parts[2][0]
                            if sign in ['-','+']:
                                addon = float(re.sub('[^0-9\.]','',parts[2]))
                                if sign == '-':
                                    opt_price = str(float(price) - addon)
                                else:
                                    if i == total:
                                        opt_price = str(addon)
                                    else:
                                        opt_price = str(float(opt_price) + addon)
                        if float(opt_price) > 0.00:
                            l = ProductLoader(item=Product(), response=response)
                            l.add_value('name', opt_name)
                            l.add_value('url', url)
                            l.add_value('price', opt_price)
                            yield l.load_item()
         else:
             if float(price) > 0.00:
                 l = ProductLoader(item=Product(), response=response)
                 l.add_value('name', name)
                 l.add_value('url', url)
                 l.add_value('price', price)
                 yield l.load_item()
