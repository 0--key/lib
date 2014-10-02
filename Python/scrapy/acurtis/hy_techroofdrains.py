import re

from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from product_spiders.items import Product, ProductLoader

try:
    import json
except ImportError:
    import simplejson as json


class HyTechroofdrainsSpider(CrawlSpider):
    name = 'hy-techroofdrains'
    allowed_domains = ['hy-techroofdrains.com']
    start_urls = ['http://www.hy-techroofdrains.com']

    rules = (
        Rule(
            SgmlLinkExtractor(
                deny=[r'checkout', r'customer/account', r'media']
            ),
            callback='parse_item',
            follow=True
        ),
    )

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)
        items = hxs.select("//div[@class='product-view hproduct']")
        for item in items:
            title = item.select("form/div[@id='pageTitle']/h1/text()").extract()[0]
            url = response.url
            # check if there is options element
            options = item.select("form/div[@id='pageTitle']/div[@id='addToCart']/\
                    fieldset[@id='product-options-wrapper']/dl/dd[1]/select/option")
            found_products = False
            if options:
                # find options content in JS
                scripts = hxs.select("//script")
                product_config = None
                for script in scripts:
                    script_cont = script.extract()
                    m = re.search("spConfig.*?\((.*)\)", script_cont)
                    if m:
                        product_config = m.group(1)
                if product_config:
                    product_config = json.loads(product_config)
                    child_products = product_config['childProducts']
                    attributes = product_config['attributes']
                    attr_codes = []
                    for attr_id, attr in attributes.items():
                        attr_codes.append(attr['code'])
                        if attr['code'] == 'outlet_size':
                            options = attr['options']
                            # add products
                            for option in options:
                                found_products = True

                                # id_part = str(option['products'][0])
                                title_part = option['label']
                                price = child_products[option['products'][0]]['price']
                                name = title + " " + title_part

                                l = ProductLoader(item=Product(), response=response)
                                l.add_value('identifier', str(name))
                                l.add_value('name', name)
                                l.add_value('url', url)
                                l.add_value('price', price)
                                yield l.load_item()

                    self.save_attr(attr_codes)

            if not found_products:
                l = ProductLoader(item=Product(), response=response)
                price = item.select("form/div[@id='pageTitle']/div[@id='addToCart']/\
                        div[@class='price-box']/span[@class='regular-price']/\
                        span[@class='price']/text()").extract()[0]
                l.add_value('identifier', str(title))
                l.add_value('name', title)
                l.add_value('url', url)
                l.add_value('price', price)
                yield l.load_item()

    def save_attr(seld, attr):
        handle = open('attrs', 'w+')
        if isinstance(attr, list):
            for line in attr:
                handle.write(line)
                handle.write("\n")
        else:
            handle.write(attr)
            handle.write("\n")
        handle.close()
