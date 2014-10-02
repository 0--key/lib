import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

class PetSenseDirectSpider(BaseSpider):
    name = 'petsensedirect.co.uk'
    allowed_domains = ['www.petsensedirect.co.uk']
    start_urls = ('http://www.petsensedirect.co.uk/',)

    def __init__(self, *args, **kwargs):
        super(PetSenseDirectSpider, self).__init__(*args, **kwargs)
        self.URLBASE = 'http://www.petsensedirect.co.uk/'

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        
        # categories
        hxs = HtmlXPathSelector(response)
        category_urls = hxs.select('//div[@id="top_nav"]//a[not(starts-with(@href,"javascript:"))]/@href').extract()
        for url in category_urls:
            url = urljoin_rfc(self.URLBASE, url)
            yield Request(url)

        # subcategories
        subcategory_urls = hxs.select('//div[@id="center"]//a[not(starts-with(@href,"javascript:"))]/img/../@href').extract()
        for url in subcategory_urls:
            url = urljoin_rfc(self.URLBASE + 'acatalog/', url)
            yield Request(url)

        # products
        products_urls = hxs.select('//div[@id="center"]//a[not(starts-with(@href,"javascript:"))]/img/../@href').extract()
        for url in products_urls:
            url = urljoin_rfc(self.URLBASE + 'acatalog/', url)
            yield Request(url, callback=self.parse_product, dont_filter=True)
        

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return

        # sub products
        hxs = HtmlXPathSelector(response)
        
        product_data = hxs.select('//table//b')
        try:
            name = product_data[0].select('./text()').extract()[0]
        except IndexError:
            return
        single_price = product_data.re('\xa3(.*?)<')
        multiple_prices = hxs.select('//select[@class="form_input_general"]/option/text()').extract()
        

        
        products_data = []

        if single_price:
            price = single_price[0]
            products_data.append((name.strip(), price))
        else:
            for name_and_price in multiple_prices:
                name_and_price = re.search('(.*).*\xa3(.*)', name_and_price)
                if name_and_price:
                    name_and_price = name_and_price.groups()
                    products_data.append((name.strip() + ' ' + name_and_price[0].strip(), name_and_price[1]))

        for item in products_data:
            product = Product()
            loader = ProductLoader(item=product, response=response)
            # try:
            loader.add_value('url', response.url)
            loader.add_value('name', item[0])
            loader.add_value('price', item[1])

            loader.add_value('sku', '')

            yield loader.load_item()
            # except IndexError:
                # continue
  
    