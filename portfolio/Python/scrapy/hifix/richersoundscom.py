import logging

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.utils import extract_price

from product_spiders.items import Product, ProductLoader


class RichersoundsComSpider(BaseSpider):
    name = 'richersounds.com'
    allowed_domains = ['richersounds.com']
    start_urls = ('http://richersounds.com',)
    clearance_start_urls = ('http://www.richersounds.com/clearance', )

    all_products_suffix = '/?products=ALL'

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, self.parse, meta={'dont_merge_cookies': True})
        for url in self.clearance_start_urls:
            yield Request(url, self.parse_clearance, dont_filter=True, meta={'dont_merge_cookies': True})

    def parse_clearance(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # regions
        region_urls = hxs.select("//dl[@id='regionList']/dd/a/@href").extract()
        for url in region_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url, callback=self.parse_clearance, meta={'dont_merge_cookies': True})

        # stores
        store_urls = hxs.select("//div[@class='clearanceRegion']//ul/li/a/@href").extract()
        for url in store_urls:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url, callback=self.parse_clearance, meta={'dont_merge_cookies': True})

        # products list
        products = hxs.select("//ul[@class='prodListClear']/li[position() > 1]/dl/dt/a/@href").extract()
        if not products and not store_urls and not region_urls:
            logging.error("ERROR!! NO PRODUCTS 1!! %s " % response.url)
        for url in products:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url, meta={'dont_merge_cookies': True}, callback=self.parse_product_clearance)
        #for product_el in products:
            #name = product_el.select("dt/a/text()").extract()
            #if not name:
                #logging.error("ERROR!! NO NAME CLEARANCE!! %s" % (response.url, ))
                #continue
            #name = " ".join(name) + " clearance"

            #url = product_el.select("dt/a/@href").extract()
            #if not url:
                #logging.error("ERROR!! NO URL CLEARANCE!! %s %s" % (response.url, name))
                #continue
            #url = url[0]
            #url = urljoin_rfc(URL_BASE, url)

            #price = product_el.select("dd[last()]/text()").extract()
            #if not price:
                #logging.error("ERROR!! NO PRICE CLEARANCE!! %s %s" % (response.url, name))
                #continue

            #product = Product()
            #loader = ProductLoader(item=product, response=response)
            #loader.add_value('url', url)
            #loader.add_value('name', name)
            #loader.add_value('price', price)
            #yield loader.load_item()
            #product_count += 1

        if products:
            # pages
            page_urls = hxs.select("//div[@class='pageList']//a/@href").extract()
            for url in page_urls:
                url = urljoin_rfc(URL_BASE, url)
                yield Request(url, callback=self.parse_clearance, meta={'dont_merge_cookies': True})

    def parse(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # categories
        category_urls = hxs.select("//ul[@class='topMenu']/li/h3/a/@href | \
                                    //ul[@class='topMenu']/li//ul/li/a/@href").extract()
        for url in category_urls:
            url = urljoin_rfc(URL_BASE, url)
            if url.find(self.all_products_suffix) < 0:
                url += self.all_products_suffix
            yield Request(url, meta={'dont_merge_cookies': True})

        hot_deal_products = hxs.select("//div[contains(@class, 'infiniteCarousel')]//li/div[@class='hpproduct']/a[1]/@href").extract()
        for url in hot_deal_products:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url, meta={'dont_merge_cookies': True}, callback=self.parse_product)
            #name = product_el.select("a[1]//text()").extract()
            #if not name:
                #logging.error("ERROR!! NO NAME HOT DEALS!! %s" % (response.url, ))
                #continue
            #name = " ".join([x.strip() for x in name])

            #url = product_el.select("a[1]/@href").extract()
            #if not url:
                #logging.error("ERROR!! NO URL HOT DEALS!! %s %s" % (response.url, name))
                #continue
            #url = url[0]
            #url = urljoin_rfc(URL_BASE, url)

            #price = product_el.select("div[@class='pricing']/h4/a/text()").extract()
            #if not price:
                #logging.error("ERROR!! NO PRICE HOT DEALS!! %s %s" % (response.url, name))
                #continue
            #price = price[0]

            #product = Product()
            #loader = ProductLoader(item=product, response=response)
            #loader.add_value('url', url)
            #loader.add_value('name', name)
            #loader.add_value('price', price)
            #yield loader.load_item()

        clearance_products = hxs.select("//div[@class='clearance-plist']//ul[@class='products']/li/h2/a/@href").extract()
        for url in clearance_products:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url, meta={'dont_merge_cookies': True}, callback=self.parse_product_clearance)
        #for product_el in clearance_products:
            #name = product_el.select("h2/a/text()").extract()
            #if not name:
                #continue
            #name = " ".join([x.strip() for x in name]) + " clearance"

            #url = product_el.select("h2/a/@href").extract()
            #if not url:
                #logging.error("ERROR!! NO URL 1!! %s %s" % (response.url, name))
                #continue
            #url = url[0]
            #url = urljoin_rfc(URL_BASE, url)

            #price = product_el.select("span[@class='price']/text()").extract()
            #if not price:
                #logging.error("ERROR!! NO PRICE 1!! %s %s" % (response.url, name))
                #continue
            #price = price[0]
            #if not price:
                #logging.error("ERROR!! NO PRICE 1!! %s %s" % (response.url, name))
                #continue

            #product = Product()
            #loader = ProductLoader(item=product, response=response)
            #loader.add_value('url', url)
            #loader.add_value('name', name)
            #loader.add_value('price', price)
            #yield loader.load_item()

        products = hxs.select("//ul[contains(@class, 'pList')]/li/div[@class='product-content']//a[@class='product-info']/@href").extract()
        for url in products:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url, meta={'dont_merge_cookies': True}, callback=self.parse_product)
        #for product_el in products:
            #name = product_el.select(".//h2[@class='product-title-info']//span[@class='title']/text()").extract()
            #if not name:
                #logging.error("ERROR!! NO NAME!! %s" % (response.url,))
                #continue
            #name = " ".join([x.strip() for x in name])

            #url = product_el.select(".//a[@class='product-info']/@href").extract()
            #if not url:
                #logging.error("ERROR!! NO URL!! %s %s" % (response.url, name))
                #continue
            #url = url[0]
            #url = urljoin_rfc(URL_BASE, url)

            #price = product_el.select("div[@class='price-block']/h4/text()").extract()
            #if not price:
                #logging.error("ERROR!! NO PRICE!! %s %s" % (response.url, name))
                #continue
            #price = price[0]

            #product = Product()
            #loader = ProductLoader(item=product, response=response)
            #loader.add_value('url', url)
            #loader.add_value('name', name)
            #loader.add_value('price', price)
            #yield loader.load_item()

        if not products and not hot_deal_products and not clearance_products:
            logging.error("ERROR!! NO PRODUCTS!! %s " % response.url)

    def parse_product(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        name = hxs.select("//span[@class='product-title']/text()").extract()
        if not name:
            logging.error("ERROR!! NO NAME PRODUCT PAGE!! %s" % (response.url, ))
            return
        name = " ".join([x.strip() for x in name])

        url = response.url

        price = hxs.select("//span[@class='biggerPrice']/text()").extract()
        if not price:
            logging.error("ERROR!! NO PRICE PRODUCT PAGE!! %s %s" % (response.url, name))
            return
        price = extract_price(price[0].strip())
        if not price:
            logging.error("ERROR!! NO PRICE PRODUCT PAGE!! %s %s" % (response.url, name))
            return

        product = Product()
        loader = ProductLoader(item=product, response=response)
        loader.add_value('url', url)
        loader.add_value('name', name)
        loader.add_value('price', price)
        yield loader.load_item()

    def parse_product_clearance(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        name = hxs.select("//div[contains(@class, 'prodDetails')]/h2/text()").extract()
        if not name:
            logging.error("ERROR!! NO NAME PRODUCT PAGE!! %s" % (response.url, ))
            return
        name = " ".join([x.strip() for x in name])

        url = response.url

        price = hxs.select("//div[@class='pricing']/h4/text()").extract()
        if not price:
            logging.error("ERROR!! NO PRICE PRODUCT PAGE!! %s %s" % (response.url, name))
            return
        price = extract_price(price[0].strip())
        if not price:
            logging.error("ERROR!! NO PRICE PRODUCT PAGE!! %s %s" % (response.url, name))
            return

        product = Product()
        loader = ProductLoader(item=product, response=response)
        loader.add_value('url', url)
        loader.add_value('name', name)
        loader.add_value('price', price)
        yield loader.load_item()
