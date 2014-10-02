import re
import logging
from decimal import Decimal

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader


class FirstincoffeeComSpider(BaseSpider):
    name = '1stincoffee.com'
    allowed_domains = ['1stincoffee.com']
    start_urls = ('http://www.1stincoffee.com/search_results.asp?txtsearchParamTxt=&txtsearchParamCat=ALL&btnSearch.x=6&btnSearch.y=8&txtsearchParamType=ALL&iLevel=1&txtsearchParamMan=ALL&txtsearchParamVen=ALL&txtFromSearch=fromSearch',)

    def parse(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # pages
        page_urls = hxs.select("//td[@class='tdContent2']/table//a/@href").extract()
        for url in page_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        products = hxs.select("//td[@class='tdContent2']/form/table/tr[1]")
        if not products:
            print "ERROR!! NO PRODUCTS!! %s " % response.url
            logging.error("ERROR!! NO PRODUCTS!! %s" % response.url)
        for product_el in products:
            name = product_el.select("td/b[1]/font/text()").extract()
            if not name:
                logging.error("ERROR!! NO NAME!! %s " % response.url)
                continue
            name = name[0]

            url = product_el.select("td/a/@href").extract()
            if not url:
                url = response.url
            else:
                url = url[0]
                url = urljoin_rfc(URL_BASE, url)

            price = product_el.select("td/text() |\
                                       td/font/b/text() |\
                                       td/p/text()").extract()
            if not price:
                logging.error("ERROR!! NO PRICE!! %s, %s " % (response.url, name))
                continue
            price = "".join(price)
            m = re.search("\$([\d\.,]*)", price)
            if not m:
                logging.error("ERROR!! NO PRICE!! %s, %s " % (response.url, name))
                continue
            price = m.group(1)

            options = product_el.select(".//select/option/text()").extract()
            if options:
                for option in options:
                    m = re.search("([^(]*)(\([^)]*\$([\d\.,]*)[^)]*\))?", option)
                    if not m:
                        logging.error("ERROR!! NO PRICE!! %s, %s " % (response.url, name))
                        continue
                    name2, add_text, price2 = m.groups()
                    product_name = "%s, %s" % (name, name2)
                    product_price = Decimal(price.replace(",", ""))
                    if price2:
                        product_price += Decimal(price2)
                    product = Product()
                    loader = ProductLoader(item=product, response=response)
                    loader.add_value('url', url)
                    loader.add_value('name', product_name)
                    loader.add_value('price', product_price)
                    loader.add_value('sku', '')
                    yield loader.load_item()

            else:
                product = Product()
                loader = ProductLoader(item=product, response=response)
                loader.add_value('url', url)
                loader.add_value('name', name)
                loader.add_value('price', price)
                loader.add_value('sku', '')
                yield loader.load_item()

    def parse_old(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # categories
        category_urls = hxs.select("//div[@id='leftnav']/ul[position()<last()]/li/a/@href").extract()
        for url in category_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url)

        # products list
        products = hxs.select("//div[@class='productdiv']/table[@class='threecell']/tr/td")
        if not products:
            products = hxs.select("//div[@id='content']/table[@class='threecell']/tr/td")
            if not products:
                print "ERROR!! NO PRODUCTS!! %s " % response.url
                logging.error("ERROR!! NO PRODUCTS!! %s" % response.url)
        for product_el in products:
            name = product_el.select("h3/text()").extract()
            if name:
                name = [x.strip() for x in name]
                name = " ".join(name)

                url = product_el.select("a[1]/@href").extract()
                if not url:
                    print "ERROR!! NO URL!! %s" % response.url
                    logging.error("ERROR!! NO URL!! %s, %s" % (name, response.url))
                    continue
                url = url[0]
                url = urljoin_rfc(URL_BASE, url)

                price = product_el.select("span/text()").extract()
                if not price:
                    yield Request(url, callback=self.parse_product)
#                    print "ERROR!! NO PRICE!! %s" % response.url
#                    logging.error("ERROR!! NO PRICE!! %s, %s" % (name, response.url))
                    continue
                price = [x.strip() for x in price]
                price = "".join(price)

                m = re.search("(starting|available|sizes)", price, re.IGNORECASE)
                if m:
                    yield Request(url, callback=self.parse_product)
                    continue

                m1 = re.search("(.*?(can|pound|oz|bag|brick|pack|jar|filter)+.*?)(for)?[\s]*(\$?[\d,\.]+)[\s]*$", price, re.IGNORECASE)
                m2 = re.search("^[\s]*(\$?[\d,\.]+)(.*?(can|oz|bag|brick|pound|kilo|pack|jar|filter)+.*?)", price, re.IGNORECASE)
                m = re.search("(\$?[\d]+[\d,\.]+)$", price)
                if m1:
                    name += ", %s" % m1.group(1).strip()
                    price = m1.group(4)
                elif m2:
                    name += ", %s" % m2.group(2).strip()
                    price = m2.group(1)
                elif m:
                    price = m.group(1)
                else:
                    yield Request(url, callback=self.parse_product)
#                    print "ERROR!! NO PRICE!! %s" % response.url
#                    logging.error("ERROR!! NO PRICE!! %s, %s" % (name, response.url))
                    continue

                product = Product()
                loader = ProductLoader(item=product, response=response)
                loader.add_value('url', url)
                loader.add_value('name', name)
                loader.add_value('price', price)
                loader.add_value('sku', '')
                yield loader.load_item()

            else:
                # if refurbished products
                name = product_el.select("a[1]/text()").extract()
                if not name:
                    print "ERROR!! NO NAME 2!! %s" % response.url
                    logging.error("ERROR!! NO NAME 2!! %s" % response.url)
                    continue
                name = [x.strip() for x in name]
                name = name[0].strip().strip("-")

                url = product_el.select("a[1]/@href").extract()
                if not url:
                    print "ERROR!! NO URL 2!! %s" % response.url
                    logging.error("ERROR!! NO URL 2!! %s, %s" % (name, response.url))
                    continue
                url = url[0]
                url = urljoin_rfc(URL_BASE, url)

                price = product_el.select("a/strong/text()").extract()
                if not price:
                    yield Request(url, callback=self.parse_product)
#                    print "ERROR!! NO PRICE 2!! %s" % response.url
#                    logging.error("ERROR!! NO PRICE 2!! %s, %s" % (name, response.url))
                    continue
                price = price[0]

                m = re.search("(\$?[0-9\.]*)", price)
                if m:
                    price = m.group(1)
                else:
                    yield Request(url, callback=self.parse_product)
#                    print "ERROR!! NO PRICE 2!! %s" % response.url
#                    logging.error("ERROR!! NO PRICE 2!! %s, %s" % (name, response.url))
                    continue

                product = Product()
                loader = ProductLoader(item=product, response=response)
                loader.add_value('url', url)
                loader.add_value('name', name)
                loader.add_value('price', price)
                loader.add_value('sku', '')
                yield loader.load_item()

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)

        name = hxs.select("//div[@id='pricetext']/b/text()").extract()
        if not name:
            print "ERROR!! NO NAME!! %s" % response.url
            logging.error("ERROR!! NO NAME!! %s, %s" % (name, response.url))
            return
        name = [x.strip() for x in name]
        name = name[0]

        url = response.url

        names2 = hxs.select("//div[@id='pricetext']/span[@class='style1']/text()").extract()
        price_position = 1
        if names2:
            prices = hxs.select("//div[@id='pricetext']/text()").extract()
            for name2 in names2:
                name += " %s" % name2.strip()
                price = prices[price_position]
                product = Product()
                loader = ProductLoader(item=product, response=response)
                loader.add_value('url', url)
                loader.add_value('name', name)
                loader.add_value('price', price)
                loader.add_value('sku', '')
                yield loader.load_item()
                price_position+=1
        else:
            prices = hxs.select("//div[@id='pricetext']/text()").extract()
            if len(prices) > (price_position+1):
                for i in range(price_position, len(prices)-1):
                    m = re.search("(.*?):[\s]*(\$?[\d,.]+)$", prices[i])
                    if m:
                        name += m.group(1).strip()
                        price = m.group(2)
                        product = Product()
                        loader = ProductLoader(item=product, response=response)
                        loader.add_value('url', url)
                        loader.add_value('name', name)
                        loader.add_value('price', price)
                        loader.add_value('sku', '')
                        yield loader.load_item()
            else:
                price = prices[price_position]
                product = Product()
                loader = ProductLoader(item=product, response=response)
                loader.add_value('url', url)
                loader.add_value('name', name)
                loader.add_value('price', price)
                loader.add_value('sku', '')
                yield loader.load_item()
