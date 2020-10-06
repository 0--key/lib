from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy.http import FormRequest

class HTFR(BaseSpider):
    name = 'htfr.com-soundslive'
    allowed_domains = ['htfr.com', 'www.htfr.com']
    start_urls = ['http://www.htfr.com/pages/browseMedia.php?type=genre']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        relative_urls = hxs.select('//div[@id="tabs-genre"]//ul[@class="browseResultLinks"]/li/a/@href').extract()
        url = urljoin_rfc('http://www.htfr.com/',
                           relative_urls[0], response.encoding)
        yield Request(url, callback = self.parse_pages,
                      meta = {  'urls': relative_urls[1:]})
  
    def parse_pages(self, response):
        URL_BASE = 'http://www.htfr.com/'
               
        hxs = HtmlXPathSelector(response)
        products = hxs.select('//div[@class="productItem rectangle nocat"]')
        if not products:
            products = hxs.select('//div[@class="productItem square"]')
        if not products:
            products = hxs.select('//div[@class="productItem square nocat"]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            loader.add_xpath('name', './/h4/a/text()')
            url = product.select('.//h4/a/@href')[0].extract()
            url = urljoin_rfc(URL_BASE, url)
            loader.add_value('url', url)
            price = product.select('.//h5[@class="prodPrice"]/text()').extract()
            if not price:
                price = product.select('.//h5[@class="prodPrice"]/span/text()').extract()
            loader.add_value('price', price)
            yield loader.load_item()
       
        #next page
        next_page = hxs.select('//div[@class="paginationLinkNext"]/a/@href').extract()
        if next_page:
            url = urljoin_rfc(URL_BASE, next_page[0])
            yield Request(url, callback = self.parse_pages, dont_filter=True, meta = {'urls': response.meta['urls']})
        else:
            if 'urls' in response.meta:
                if  response.meta['urls'][1:]:
                    url = urljoin_rfc(URL_BASE,
                                      response.meta['urls'][0], response.encoding)
                    yield Request(url, callback=self.parse_pages, 
                                  meta = {'urls': response.meta['urls'][1:]})
                else:
                    if response.meta['urls']:
                        url = urljoin_rfc(URL_BASE,
                                          response.meta['urls'][0], response.encoding)
                        yield Request(url, callback=self.parse_pages,  meta = {'urls': []})
            
