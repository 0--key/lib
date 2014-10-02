from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader


class KatomSpider(BaseSpider):
    name = 'katom.com'
    allowed_domains = ['katom.com']
    start_urls = ('http://www.katom.com/products.A.1.html',)

    def parse(self, response):
      hxs = HtmlXPathSelector(response)

      alphanums = hxs.select('//div[@class="sub_navigation"]//a/@href').extract()
      for url in alphanums:
        yield Request(url, callback=self.parse_char)

      products = hxs.select('//div[@class="column1" or @class="column2"]//a/@href').extract()
      for url in products:
        yield Request(url, callback=self.parse_product)

    def parse_char(self, response):
      hxs = HtmlXPathSelector(response)
      base_url = get_base_url(response)

      products = hxs.select('//div[@class="column1" or @class="column2"]//a/@href').extract()
      for url in products:
        yield Request(url, callback=self.parse_product)

      next_page = hxs.select('//div[@class="paginate_nav_up"]/b/following-sibling::a[1]/@href').extract()
      if next_page:
        yield Request(urljoin_rfc(base_url, next_page[0]), callback=self.parse_char)

    def parse_product(self, response):
      hxs = HtmlXPathSelector(response)

      loader = ProductLoader(item=Product(), response=response)
      loader.add_value('url', response.url)
      loader.add_xpath('name', '//h1[@id="top_product_info_block_product_title_text"]/text()')
      loader.add_xpath('sku', '//ul[@id="top_product_info_block_product_data_list"]/li/strong/text()')
      loader.add_xpath('price', '//p[@id="top_product_info_block_product_data_new_low_price"]/text()')
      yield loader.load_item()
