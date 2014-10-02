from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader



class AblekitchenSpider(BaseSpider):
    name = 'ablekitchen.com'
    allowed_domains = ['ablekitchen.com']
    start_urls = ('http://www.ablekitchen.com',)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        '''
        categories = hxs.select('//a[@class="nav_link"]/@href').extract()
        for category in categories:
            yield Request(category)

        subcategories = hxs.select('//a[@class="expand_link" and contains(text(), "Sub Categories")]/' +
                                   'ancestor::div[contains(@class, "expand_title")]/' +
                                   'following-sibling::div[@class="expand_body"]//' +
                                   'div[@class="leftscroll_text_subcategory"]//a/@href').extract()

        for subcategory in subcategories:
            yield Request(subcategory)
        '''
        categories = ['http://www.ablekitchen.com/equipment/v22/WINCO.html',
                      'http://www.ablekitchen.com/equipment/v17/Thunder-Group.html',
                      'http://www.ablekitchen.com/equipment/v1002/Cardinal.html',
                      'http://www.ablekitchen.com/equipment/v1004/Libbey-Glass.html',
                      'http://www.ablekitchen.com/equipment/v5656/Friedr-Dick.html',
                      'http://www.ablekitchen.com/equipment/v36/Cecilware-Corp.html',
                      'http://www.ablekitchen.com/equipment/v70/Turbo-Air.html',
                      'http://www.ablekitchen.com/equipment/v58/Eastern-Tabletop.html',
                      'http://www.ablekitchen.com/equipment/v9/G-E-T.html',
                      'http://www.ablekitchen.com/equipment/v5661/Bakers-Pride-Restaurant-Equipment.html']

        categories = [cat + '?per_page=192' for cat in categories]

        for category in categories:
            yield Request(category)

        next_page = hxs.select('//td[@class="next"]/a[@class="pagerlink"]/@href').extract()
        if next_page:
            yield Request(next_page[0])

        for product in self.parse_products(hxs):
            yield product

    def parse_products(self, hxs):
        products = hxs.select('//li[contains(@itemtype, "Product")]')
        for product in products:
            product_loader = ProductLoader(Product(), product)
            product_loader.add_xpath('name', './/a[@itemprop="name"]/text()')
            product_loader.add_xpath('url', './/a[@itemprop="name"]/@href')
            product_loader.add_xpath('price', './/span[@itemprop="price"]/text()')
            sku = product.select('.//span[@itemprop="model"]/text()')
            if sku:
                sku = sku.extract()[0]
                dash_pos = sku.find('-')
                if dash_pos >= 0:
                    sku = sku[dash_pos + 1:]
                product_loader.add_value('sku', sku)

            yield product_loader.load_item()
