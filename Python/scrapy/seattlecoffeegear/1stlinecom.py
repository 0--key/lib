import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

import logging

prices_range_regex = "\$[\d,]*\.\d*\s*-\s*\$[\d,]*\.\d*"
price_regex = "\$[\d,]*\.\d*"
price_regex_product_page = "[\d,]*\.\d*\s*US Dollars"


class FirstLineComSpider(BaseSpider):
    name = '1st-line.com'
    allowed_domains = ['1st-line.com']
    start_urls = ('http://www.1st-line.com/education/fundamentals.html',)

    product_lists_urls = (
        'http://www.1st-line.com/machines/comm_mod/grinder/byprice.htm',
        'http://www.1st-line.com/machines/machinebyprice.htm',
        'http://www.1st-line.com/machines/home_mod/ascaso/index.htm'
        'http://www.1st-line.com/machines/home_mod/baratza/index.htm'
        'http://www.1st-line.com/machines/home_mod/capresso/index.htm'
        'http://www.1st-line.com/machines/home_mod/elektra/index.htm'
        'http://www.1st-line.com/machines/home_mod/isomac/index.htm'
        'http://www.1st-line.com/machines/home_mod/jura/index.htm'
        'http://www.1st-line.com/machines/home_mod/lapavoni/index.htm'
        'http://www.1st-line.com/machines/home_mod/lelit/index.htm'
        'http://www.1st-line.com/machines/home_mod/ponte_vecchio/index.htm'
        'http://www.1st-line.com/machines/home_mod/rancilio/index.htm'
        'http://www.1st-line.com/machines/home_mod/saeco/index.htm'
        'http://www.1st-line.com/machines/home_mod/bezzera/index.htm'
        'http://www.1st-line.com/machines/comm_mod/esprmach/didiesse/index.htm',
        'http://www.1st-line.com/machines/home_mod/ecm/ECM_Veronica.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/elektra_espresso_machines/index.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/faema/index.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/fiorenzato/index.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/la-nuova-era/index.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/lapavoni/index.htm',
        'http://www.1st-line.com/machines/home_mod/laspaziale/index.htm',
        'http://www.1st-line.com/machines/home_mod/pasquini/index.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/index.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/ecm/index.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/segafredocoffeesystems/segafredo_SZ01.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/vibiemme/index.htm',
        'http://www.1st-line.com/machines/comm_mod/grinder/foodservice.htm',
        'http://www.1st-line.com/machines/comm_mod/grinder/retail.htm',
        'http://www.1st-line.com/machines/comm_mod/grinder/index.htm',
        'http://www.1st-line.com/machines/home_mod/baratza/index.htm',
        'http://www.1st-line.com/machines/home_mod/compak/index.htm',
        'http://www.1st-line.com/machines/home_mod/macap/index.htm',
        'http://www.1st-line.com/machines/comm_mod/grinder/mahlkonig/mahlkonig_index.htm',
        'http://www.1st-line.com/machines/home_mod/mazzer/index.htm',
        'http://www.1st-line.com/parts/ConceptArt.htm',
        'http://www.1st-line.com/parts/other/bases.htm',
        'http://www.1st-line.com/machines/home_mod/eg/cofstrge.htm',
        'http://www.1st-line.com/parts/urnex/index.htm',
        'http://www.1st-line.com/machines/home_mod/eg/cups/index.htm',
        'http://www.1st-line.com/machines/home_mod/eg/knockbox.htm',
        'http://www.1st-line.com/machines/home_mod/eg/pitchers.htm',
        'http://www.1st-line.com/parts/other/scoops.htm',
        'http://www.1st-line.com/machines/home_mod/eg/demispns.htm',
        'http://www.1st-line.com/parts/other/V614_filterholder_rubber_support_mat.htm',
        'http://www.1st-line.com/parts/other/aluminumtampers.htm',
        'http://www.1st-line.com/parts/other/thermometers.htm',
        'http://www.1st-line.com/parts/other/digitaltimers.htm',
        'http://www.1st-line.com/machines/home_mod/eg/travel/7027.htm',
        'http://www.1st-line.com/parts/watsftnr.htm',
        'http://www.1st-line.com/coffee/espresso/bean/bristot_index.htm',
        'http://www.1st-line.com/coffee/espresso/bean/essse_index.htm',
        'http://www.1st-line.com/coffee/espresso/bean/illy_index.htm',
        'http://www.1st-line.com/coffee/espresso/bean/lavazza_index.htm',
        'http://www.1st-line.com/coffee/espresso/bean/miscela-d%27oro_index.htm',
        'http://www.1st-line.com/coffee/espresso/bean/orocaffe_index.htm',
        'http://www.1st-line.com/tea/redespresso_index.htm',
        'http://www.1st-line.com/coffee/espresso/bean/segafred.htm',
        'http://www.1st-line.com/coffee/espresso/pod/pods.htm',
        'http://www.1st-line.com/coffee/greenbns/retail.htm',
        'http://www.1st-line.com/coffee/syrups/syrups.htm',
        'http://www.1st-line.com/machines/home_mod/homedrip.htm',
        'http://www.1st-line.com/machines/comm_mod/regcoffee/index.htm',
        'http://www.1st-line.com/machines/comm_mod/regcoffee/index_airpot.htm',
        'http://www.1st-line.com/machines/comm_mod/regcoffee/index_accessor.htm',
        'http://www.1st-line.com/machines/comm_mod/freezers/index.htm',
        'http://www.1st-line.com/blenders-mixers/index.htm',
        'http://www.1st-line.com/machines/comm_mod/bevdispensers/index.htm',
        'http://www.1st-line.com/machines/comm_mod/granita/index.htm',
        'http://www.1st-line.com/machines/home_mod/capresso/201.htm',
        'http://www.1st-line.com/machines/comm_mod/milkcont/index.htm',
        'http://www.1st-line.com/machines/comm_mod/paninigrills/index.htm',
        'http://www.1st-line.com/machines/home_mod/pasquini/k2.htm',
    )

    products_list_no_links_urls = (
        'http://www.1st-line.com/machines/comm_mod/esprmach/elektra_espresso_machines/grinders.htm',
        'http://www.1st-line.com/machines/home_mod/laspaziale/index.htm',
    )

    product_list_columns_urls = (
        'http://www.1st-line.com/machines/home_mod/elektra/elektra_base.htm',
    )

    product_list_grinders_urls = (
        'http://www.1st-line.com/machines/home_mod/indxgrnd.htm',
    )

    product_list_coffee_urls = (
        'http://www.1st-line.com/coffee/espresso/bean/illy_index.htm',
    )

    products_urls = (
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/Classe10_S2.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/Classe10_S3.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/Classe10_S4.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/Classe10_USB2.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/Classe10_USB3.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/Classe10_USB4.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/Classe10_RE2.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/Classe10_RE3.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/Classe10_RE4.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/Rancilio-Classe-9-S-espresso-machine.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/Rancilio-Classe-9-USB-espresso-machine.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/Rancilio-Classe-7-S-espresso-machine.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/Rancilio-Classe-7-E-espresso-machine.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/epoca_S2.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/epoca_E2.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/epoca_S1_tank.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/epoca_S1.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/epoca_E1.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/Rancilio-Egro-One-Pure-Coffee.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/Rancilio-Egro-One-Quick-Milk.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/Rancilio-Egro-One-Top-Milk.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/Rancilio-Egro-One-Top-Milk-XP.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/vibiemme/vibiemme_electronic_stainless.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/vibiemme/vibiemme_manual_stainless.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/vibiemme/vibiemme_direct.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/vibiemme/juniorhx.html',
        'http://www.1st-line.com/machines/comm_mod/grinder/rancilio-md40.htm',
        'http://www.1st-line.com/machines/home_mod/baratza/Baratza-Virtuoso-Preciso.htm',
        'http://www.1st-line.com/machines/home_mod/baratza/Baratza-Vario-W.htm',
        'http://www.1st-line.com/machines/home_mod/rancilio/rocky_sd.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/fiorenzato/fiorenzato_ducale.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/fiorenzato/fiorenzato_ducale_compact.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/la-nuova-era/la-nuova-era-cuadra-espresso-machine.htm',
    )

    several_products_single_product_page_urls = (
        'http://www.1st-line.com/machines/home_mod/quamar/quamar-M80.htm',
        'http://www.1st-line.com/machines/home_mod/lapavoni/la_pavoni_jolly.htm'
    )

    table_options_single_product_page_urls = (
        'http://www.1st-line.com/machines/home_mod/ascaso/ascaso_i-1_i-1d.htm',
        'http://www.1st-line.com/machines/home_mod/ascaso/ascaso_i-2_i-2d.htm'
    )

    table_options_type2_single_product_page_urls = (
        'http://www.1st-line.com/homemachines/dreamup.html',
    )

    ignore_urls = (
        'http://www.1st-line.com/machines/comm_mod/esprmach/rancilio/index.htm',
        'http://www.1st-line.com/machines/home_mod/baratza/index.htm',
        'http://www.1st-line.com/machines/comm_mod/esprmach/vibiemme/index.htm',

    )

    download_delay = 2

    def start_requests(self):
        for url in self.ignore_urls:
            yield Request(url, callback=self.dump_parse)

        for url in self.several_products_single_product_page_urls:
            yield Request(url, callback=self.parse_several_products_single_product_page)

        for url in self.table_options_single_product_page_urls:
            yield Request(url, callback=self.parse_table_options_single_product_page)

        for url in self.table_options_type2_single_product_page_urls:
            yield Request(url, callback=self.parse_table_options_type2_single_product_page)

        for url in self.products_list_no_links_urls:
            yield Request(url, callback=self.parse_product_list_no_links)

        for url in self.products_urls:
            yield Request(url, callback=self.parse_product_list)



        for url in self.product_list_grinders_urls:
            yield Request(url, callback=self.parse_product_list_grinders)

        for url in self.product_list_columns_urls:
            yield Request(url, callback=self.parse_product_list_columns)

        for url in self.products_list_no_links_urls:
            yield Request(url, callback=self.parse_product_list_no_links)

        for url in self.product_list_coffee_urls:
            yield Request(url, callback=self.parse_product_list_coffee)

        for url in self.product_lists_urls:
            yield Request(url, callback=self.parse_product_list)

    def parse_product_list(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # select 'p' elements which have 'a' as first child and 'strong' as last
        # using to filter one-product pages
        products = hxs.select("//table[@class='product_body']//td/p[*[1][local-name()='a']][*[position()=2][local-name()='strong']] |\
                               //table[@class='product_body']//td/p[*[1][local-name()='a']][*[last()][local-name()='strong']]")
        products_count = 0
        for product_el in products:
            name = product_el.select("a//text()").extract()
            if not name or not name[0].strip():
                logging.error("ERROR!! NO NAME!! %s" % (response.url, ))
                continue
            name = name[0]

            url = product_el.select("a/@href").extract()
            if not url:
                logging.error("ERROR!! NO URL!! %s %s" % (response.url, name))
                print
                continue
            url = url[0]
            url = urljoin_rfc(URL_BASE, url)

            price = product_el.select('strong/text()').extract()
            if not price:
                logging.error("ERROR!! NO PRICE!! %s %s" % (name, response.url))
                continue

            price = price[0]
            if re.search(prices_range_regex, price):
                yield Request(url, callback=self.parse_product_list)
                continue

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)
            loader.add_value('sku', '')
            yield loader.load_item()
            products_count += 1

        products2 = hxs.select("//table[@class='product_body']//td/p/strong[*[1][local-name()='a']]")
        for product_el in products2:
            name = product_el.select("a//text()").extract()
            if not name or not name[0].strip():
                logging.error("ERROR!! NO NAME!! %s" % (response.url, ))
                continue
            name = name[0]

            url = product_el.select("a/@href").extract()
            if not url:
                logging.error("ERROR!! NO URL!! %s %s" % (response.url, name))
                continue
            url = url[0]
            url = urljoin_rfc(URL_BASE, url)

            price = product_el.select('text()').extract()
            if not price:
                logging.error("ERROR!! NO PRICE!! %s %s" % (name, response.url))
                continue

            price = price[0]

            if not re.search(price_regex, price):
                logging.error("ERROR!! NO PRICE!! %s %s" % (name, response.url))
                continue

            if re.search(prices_range_regex, price):
                yield Request(url, callback=self.parse_product_list)
                continue

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)
            loader.add_value('sku', '')
            yield loader.load_item()
            products_count += 1

        products3 = hxs.select("//table[@class='product_body']//td/p[strong[*[1][local-name()='a']]]")
        for product_el in products3:
            name = product_el.select("strong[1]/a//text()").extract()
            if not name or not name[0].strip():
                logging.error("ERROR!! NO NAME!! %s" % (response.url, ))
                continue
            name = name[0]

            url = product_el.select("strong[1]/a/@href").extract()
            if not url:
                logging.error("ERROR!! NO URL!! %s %s" % (response.url, name))
                continue
            url = url[0]
            url = urljoin_rfc(URL_BASE, url)

            price = product_el.select('strong/font/text()').extract()
            if not price:
                logging.error("ERROR!! NO PRICE!! %s %s" % (name, response.url))
                continue

            price = price[0]

            if not re.search(price_regex, price):
                logging.error("ERROR!! NO PRICE BY REGEX!! %s %s" % (name, response.url))
                continue

            if re.search(prices_range_regex, price):
                yield Request(url, callback=self.parse_product_list)
                continue

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)
            loader.add_value('sku', '')
            yield loader.load_item()
            products_count += 1

        if products_count < 1:
            url = response.url
            product_el = hxs.select("//table[@class='product_body']/tr[1]/td[2]/div | \
                                     //table[@class='product_body']/tr[1]/td[2]")
            if not product_el:
                logging.error("ERROR! No product element on single product page! %s" % (response.url, ))
                return
            product_el = product_el[0]
            name = product_el.select("p[not(@class)]/strong[1]/text()[1]").extract()
            if not name:
                logging.error("ERROR! No name! %s" % (response.url, ))
                return
            if len(name) > 1:
                # could be a product with different options or a set of different products
                price_test = product_el.select('p[1]/strong//text()').re(price_regex_product_page)
                if price_test:
                    # a set of different products or a product with one price but different options
                    names = product_el.select("p[position() != 1]/strong[1]/text()[1]").extract()
                    prices = product_el.select('p[position() != 1]/strong/text()').re(price_regex_product_page)
                    if len(names) == len(prices):
                        logging.error("One product page - set of several products: %s" % response.url)
                        # a set of different products
                        names = product_el.select("p/strong[1]/text()[1]").extract()
                        prices = product_el.select('p/strong/text()').re(price_regex_product_page)
                        for name, price in zip(names, prices):
                            product = Product()
                            loader = ProductLoader(item=product, response=response)
                            loader.add_value('url', url)
                            loader.add_value('name', name)
                            loader.add_value('price', price)
                            loader.add_value('sku', '')
                            yield loader.load_item()
                    else:
                        logging.error("One product page - one price different options: %s" % response.url)
                        # a product with one price but different options
                        name = name[0]
                        price = product_el.select('p[1]/strong//text()').re(price_regex_product_page)
                        if not price:
                            logging.error("ERROR! No price for a product with one price but different options! %s %s" % (response.url, name))
                            return
                        price = price[0]
                        for add_name in names:
                            product = Product()
                            loader = ProductLoader(item=product, response=response)
                            loader.add_value('url', url)
                            loader.add_value('name', "%s %s" % (name, add_name))
                            loader.add_value('price', price)
                            loader.add_value('sku', '')
                            yield loader.load_item()
                else:
                    logging.error("One product page - different options with prices: %s" % response.url)
                    # product with different options
                    name = name[0]
                    add_names = product_el.select("p[position() != 1]/strong[1]/text()").extract()
                    prices = product_el.select('p[position() != 1]/strong/text()').re(price_regex_product_page)
                    if len(add_names) == len(prices):
                        # options have different prices
                        for add_name, price in zip(add_names, prices):
                            product = Product()
                            loader = ProductLoader(item=product, response=response)
                            loader.add_value('url', url)
                            loader.add_value('name', "%s %s" % (name, add_name))
                            loader.add_value('price', price)
                            loader.add_value('sku', '')
                            yield loader.load_item()
                    else:
                        logging.error("ERROR! No prices for options! %s %s" % (response.url, name))
            else:
                logging.error("One product page: %s" % response.url)
                # one product without options
                name = name[0]

                price = product_el.select('p[1]/strong//text()').re(price_regex_product_page)
                if not price:
                    logging.error("ERROR! No price! %s" % (response.url, ))
                    return
                price = price[0]
                product = Product()
                loader = ProductLoader(item=product, response=response)
                loader.add_value('url', url)
                loader.add_value('name', name)
                loader.add_value('price', price)
                loader.add_value('sku', '')
                yield loader.load_item()

        else:
            logging.error("%s. Found %d products" % (response.url, products_count))

    def parse_product_list_no_links(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select("//table[@class='product_body']//td/p[*[1][local-name()='img']] | \
                               //table[@class='product_body']//td/p[strong[*[1][local-name()='img']]]")
        for product_el in products:
            name = product_el.select("strong[1]//text()").extract()
            if not name:
                logging.error("ERROR!! NO NAME!! %s" % (response.url, ))
                continue
            name = name[0]

            url = response.url

            price = product_el.select('strong[2]/text()').extract()
            if not price:
                logging.error("ERROR!! NO PRICE!! %s %s" % (name, response.url))
                continue

            price = price[0]
            if re.search(prices_range_regex, price):
                yield Request(url, callback=self.parse_product_list)
                continue

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)
            loader.add_value('sku', '')
            yield loader.load_item()

    def parse_product_list_coffee(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select("//table[@class='product_body']//td/p[*[1][local-name()='a']]")
        for product_el in products:
            name = product_el.select("strong[1]//text()").extract()
            if not name:
                logging.error("ERROR!! NO NAME!! %s" % (response.url, ))
                continue
            name = name[0]

            url = product_el.select("a/@href").extract()
            if not url:
                logging.error("ERROR!! NO NAME!! %s" % (response.url, ))
                continue
            url = url[0]

            price = product_el.select('strong[last()]/text()').extract()
            if not price:
                logging.error("ERROR!! NO PRICE!! %s %s" % (name, response.url))
                continue

            price = price[0]
            if re.search(prices_range_regex, price):
                yield Request(url, callback=self.parse_product_list)
                continue

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)
            loader.add_value('sku', '')
            yield loader.load_item()

        products = hxs.select("//table[@class='product_body']//td/p[*[1][local-name()='img']]")
        for product_el in products:
            name = product_el.select("strong[1]//text()").extract()
            if not name:
                logging.error("ERROR!! NO NAME!! %s" % (response.url, ))
                continue
            name = name[0]

            url = response.url

            price = product_el.select('strong[last()]/text()').extract()
            if not price:
                logging.error("ERROR!! NO PRICE!! %s %s" % (name, response.url))
                continue

            price = price[0]
            if re.search(prices_range_regex, price):
                yield Request(url, callback=self.parse_product_list)
                continue

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)
            loader.add_value('sku', '')
            yield loader.load_item()

    def parse_several_products_single_product_page(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select("//table[@class='product_body']/tr/td[2]/p[not(@class)][*[local-name()='strong']]")
        for product_el in products:
            name = product_el.select("strong[1]//text()").extract()
            if not name:
                logging.error("ERROR!! NO NAME!! %s" % (response.url, ))
                continue
            name = name[0]

            url = response.url

            price = product_el.select('strong[2]/text() | b[last()]/text()').extract()
            if not price:
                logging.error("ERROR!! NO PRICE!! %s %s" % (name, response.url))
                continue

            price = price[0]
            if re.search(prices_range_regex, price):
                yield Request(url, callback=self.parse_product_list)
                continue

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)
            loader.add_value('sku', '')
            yield loader.load_item()

    def parse_table_options_single_product_page(self, response):
        hxs = HtmlXPathSelector(response)
        name = hxs.select("//table[@class='product_body']/tr/td[2]/p[not(@class)][*[local-name()='strong']]/strong[1]//text()").extract()
        if not name:
            logging.error("ERROR!! NO NAME!! %s" % (response.url, ))
            return
        name = name[0]
        subproducts_container = hxs.select("//table[@class='product_body']//table[@class='product_body']")
        if not subproducts_container:
            logging.error("ERROR!! NO COLORS CONTAINER!! %s" % (response.url, ))
            return
        subproducts_container = subproducts_container[0]
        subproducts = subproducts_container.select("tr/td/p[not(@class)][*[local-name()='strong']]")
        for product_el in subproducts:
            add_name = product_el.select("strong[1]//text()").extract()
            if not add_name:
                logging.error("ERROR!! NO ADD NAME!! %s" % (response.url, ))
                continue
            add_name = add_name[0]

            url = response.url

            price = product_el.select('strong[2]//text() | b[last()]/text()').extract()
            if not price:
                logging.error("ERROR!! NO PRICE!! %s %s" % (name, response.url))
                continue

            price = price[0]
            if re.search(prices_range_regex, price):
                yield Request(url, callback=self.parse_product_list)
                continue

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', "%s %s" % (name, add_name))
            loader.add_value('price', price)
            loader.add_value('sku', '')
            yield loader.load_item()

    def parse_table_options_type2_single_product_page(self, response):
        hxs = HtmlXPathSelector(response)
        name = hxs.select("//div[@id='mainContent']/center/table/tr[1]/td[1]/p[2][not(@class)][*[local-name()='strong']]/strong[1]//text()").extract()
        if not name:
            logging.error("ERROR!! NO NAME!! %s" % (response.url, ))
            return
        name = name[0]
        subproducts = hxs.select("//div[@id='mainContent']/center/table//table[@class='product_body']/tr[position()>1]")
        for product_el in subproducts:
            add_name = product_el.select("td[1]//text()").extract()
            if not add_name:
                logging.error("ERROR!! NO NAME!! %s" % (response.url, ))
                continue
            add_name = add_name[0]

            url = response.url

            price = product_el.select('td[3]//text()').extract()
            if not price:
                logging.error("ERROR!! NO PRICE!! %s %s" % (name, response.url))
                continue

            price = price[0]
            if re.search(prices_range_regex, price):
                yield Request(url, callback=self.parse_product_list)
                continue

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', "%s %s" % (name, add_name))
            loader.add_value('price', price)
            loader.add_value('sku', '')
            yield loader.load_item()

    def parse_product_list_columns(self, response):
        hxs = HtmlXPathSelector(response)
        products_count = hxs.select("count(//table[@class='product_body']/tr[3]/td)").extract()[0]
        for i in range(1, int(float(products_count))+1):
            name = hxs.select("//table[@class='product_body']/tr[3]/td[%d]/p//text()" % i).extract()
            if not name:
                logging.error("ERROR!! NO NAME!! %s" % (response.url, ))
                continue
            name = name[0]

            url = response.url

            price = hxs.select("//table[@class='product_body']/tr[4]/td[%d]/p[1]/strong[last()]//text()" % i).extract()
            if not price:
                logging.error("ERROR!! NO PRICE!! %s %s" % (name, response.url))
                continue

            price = price[0]
            if re.search(prices_range_regex, price):
                yield Request(url, callback=self.parse_product_list)
                continue

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)
            loader.add_value('sku', '')
            yield loader.load_item()

    def parse_product_list_grinders(self, response):
        URL_BASE = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        product_links = hxs.select("//table[@class='product_body']//a/@href").extract()
        for url in product_links:
            url = urljoin_rfc(URL_BASE, url)
            yield Request(url, callback=self.parse_product_list)

    def dump_parse(self, response):
        """Used for not pages that should not be parsed
        """
        pass