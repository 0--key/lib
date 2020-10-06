from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader


class SeattlecoffeegearComSpider(BaseSpider):
    name = 'seattlecoffeegear.com'
    allowed_domains = ['seattlecoffeegear.com']
    start_urls = ('http://www.seattlecoffeegear.com/',)
    page_query = '?show=320&page='
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.19 (KHTML, like Gecko) Ubuntu/12.04 Chromium/18.0.1025.151 Chrome/18.0.1025.151 Safari/535.19'

    def parse(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # categories
        category_urls = hxs.select('//ul[@id="nav"]/li//a/@href').extract()
        for url in category_urls:
            url = urljoin_rfc(URL_BASE, url)
            url += self.page_query + str(1)
            yield Request(url)

        # sub-categories
        sub_category_urls = hxs.select("//a[@class='subcategory_link']/@href").extract()
        for url in sub_category_urls:
            url = urljoin_rfc(URL_BASE, url)
            url += self.page_query + str(1)
            yield Request(url)

        # pages
        page = 2
        page_urls = hxs.select("//div[@class='pages']//a/@href").extract()
        for url in page_urls:
            yield Request(url)
            page += 1

        # products list
        products_count = 0
        products = hxs.select('//h2[@class="product-name"]/..')
        #products = hxs.select("//form[@class='search_results_section']/table[2]/tr/td/table/tr/td/table/tr/td[@width='25%']")
        if not products:
            print "ERROR!! NO PRODUCTS!! %s " % response.url
        for product_el in products:
            name = product_el.select(".//h2/a/text()").extract()
            if not name:
                continue
            name = name[0]

            url = product_el.select(".//h2/a/@href").extract()
            if not url:
                print "ERROR!! NO URL!! %s" % response.url
                continue
            url = url[0]

            price = product_el.select('.//span[@class="price" and starts-with(@id, "product-price")]/text()').extract()
            if not price:
                price = product_el.select('.//span[@class="price"]/text()').extract()
            if not price:
                print "ERROR!! NO PRICE!! %s" % response.url
                price = '0'
            else:
                price = price[0]

            products_count += 1
            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', u' \r\n' + name + u'\r\n')
            loader.add_value('price', price)
            loader.add_value('sku', '')
            yield loader.load_item()

        if products_count == 0:
            # products list 2
            products = hxs.select("//form[@class='search_results_section']/table[2]/tr/td/table/tr/td/table/tr")
            if not products:
                print "ERROR!! NO PRODUCTS!! %s " % response.url
            for product_el in products:
                name = product_el.select("td/a[@class='productnamecolor colors_productname']/text()").extract()
                if not name:
                    continue

                url = product_el.select("td/a[@class='productnamecolor colors_productname']/@href").extract()
                if not url:
                    print "ERROR!! NO URL!! %s" % response.url
                    continue
                url = url[0]

                price = product_el.select('.//font[@class="pricecolor colors_productprice"]/text()').extract()
                if not price:
                    print "ERROR!! NO PRICE!! %s" % response.url
                    continue
                price = price[0]

                product = Product()
                loader = ProductLoader(item=product, response=response)
                loader.add_value('url', url)
                loader.add_value('name', u' \r\n' + name + u'\r\n')
                loader.add_value('price', price)
                loader.add_value('sku', '')
                yield loader.load_item()
