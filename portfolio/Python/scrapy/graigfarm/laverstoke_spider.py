import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy import log

class LaverstokeSpider(BaseSpider):
    name = 'laverstokepark.co.uk'
    allowed_domains = ['www.laverstokepark.co.uk']
    start_urls = (
                  'http://www.laverstokepark.co.uk/Beef-Pork-Lamb-Chicken/catlist_fnct480.htm',
                  'http://www.laverstokepark.co.uk/Sausages-Burgers-Bacon/catlist_fnct478.htm',
                  'http://www.laverstokepark.co.uk/BBQ-Box-Selections/prodlist_ct529.htm',
                  )
    
    def parse(self, response):
        log.msg("parse(%s)" % response.url)
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        
        regex = re.compile('(catlist|prodlist)')
        match = regex.search(response.url)
        if match:
            url_type = match.group(1)
            log.msg("URL is a %s" % url_type)
            if url_type == 'catlist':
                category_urls = hxs.select('//div[@class="catTile"]/a[@class="catTitle"]/@href').extract()                
                for cat_url in category_urls:
                    yield Request(urljoin_rfc(base_url, cat_url), callback=self.parse_category)
            elif url_type == 'prodlist':
                log.msg("Calling parse_category(%s)" % response.url)
                yield Request(response.url, callback=self.parse_category)
                
    def parse_category(self, response):
        log.msg("parse_category(%s)" % response.url)
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        regex_sku = re.compile('_(.+)\.htm$')
        
        products = hxs.select('//div[span/@class="ProductTitleHome"]')
        for product in products:
            loader = ProductLoader(item=Product(), selector=product)
            
            url = product.select('.//span[@class="ProductTitleHome"]/a/@href').extract()[0]
            loader.add_value('url', url)
            loader.add_xpath('name', './/span[@class="ProductTitleHome"]/a/text()')
            loader.add_xpath('price', './/span[@class="Price"]/text()')
            match = regex_sku.search(url)
            if match:
                loader.add_value('sku', match.group(1))
    
            yield loader.load_item()
