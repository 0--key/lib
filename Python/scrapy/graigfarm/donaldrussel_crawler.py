import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
from scrapy import log

class DonaldRusselSpider(BaseSpider):
    name = 'donaldrussell.com'
    allowed_domains = ['www.donaldrussell.com']
    start_urls = (
                  'http://www.donaldrussell.com/meat.html',
                  'http://www.donaldrussell.com/poultry-and-game.html',
                  'http://www.donaldrussell.com/fish-seafood.html',
                  )
    
    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        
        cat_urls = hxs.select('//div[@class="clist-title"]/a/@href').extract()
        log.msg("Found %d categories in %s" % (len(cat_urls), response.url))
        for cat_url in cat_urls:
            yield Request(cat_url, callback=self.parse)
            
        # First AJAX to load some sort of placeholder
        #re_ajax_url1 = re.compile("\'(http://www\.donaldrussell\.com/personalmerchantextension/event/suggest/block_names/.+)\';")
        #match_url1 = re_ajax_url1.search(response.body)
        # Second AJAX to load the products
        re_ajax_url2 = re.compile("\'(http://www.donaldrussell.com/cachemanager/block/index/block_names.+)\';")             
        match_url2 = re_ajax_url2.search(response.body)
        # Get all required variables for AJAX requests
        re_registry_data = re.compile("registry_data\[\'(\w+)\'] = \'([^\']+)\'")
        match_registries = re_registry_data.findall(response.body)
        
        #if match_url1 and match_url2 and match_registries:
        if match_url2 and match_registries:
            registry_data = {}
            for m in match_registries:
                registry_data[m[0]] = m[1]
            #if registry_data.has_key('current_category'):
                #url1 = match_url1.group(1) + "current_category/" + registry_data["current_category"] + "/"
                #yield Request(url1)
            url2 = match_url2.group(1)
            for (key, val) in registry_data.items():
                url2 += key+'/'+val+'/'
            yield Request(url2, callback=self.parse_product)
                          
            
    def parse_product(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        
        products_url = hxs.select('//li[contains(@class,"item")]//h2/a/@href').extract()
        
        for product_url in products_url:
            yield Request(product_url, callback=self.parse_product_detail)
            
        next_page = hxs.select('//div[@class="pager"]//a[@class="next"]/@href').extract()
        if(next_page):
            yield Request(next_page[0], callback=self.parse_product)
    
    def parse_product_detail(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        
        name = hxs.select('//div[@class="product-name"]/h1/text()').extract()[0]
        
        # hxs.select('//div[@class="product-name"]/h1/text()')
        simple_product = hxs.select('//script[contains(text(), "catalog_product_view_type_simple")]')
        if simple_product:
            html = simple_product.re('jQuery\(.+catalog_product_view_type_simple.+\.html\(\"(.+)\"\);')[0]
            html = self.stripslashes(html)
            hxs_item = HtmlXPathSelector(text=html)
            
            # Discounted price
            price = hxs_item.select('//span[contains(@id,"product-price")]/span/text()')
            if not price:
                # Normal price
                price = hxs_item.select('//span[contains(@id,"product-price")]/text()')
            price = price.extract()[0].strip()
            # Remove JS euro sign
            price = price.replace("u00a3","")
            
            loader = ProductLoader(item=Product(), selector=hxs_item)
            loader.add_value('name', name)
            loader.add_value('url', response.url)
            loader.add_value('price', price)
            loader.add_value('sku', simple_product.re('CODE: (\w+)'))
            yield loader.load_item()
            
        sub_products = hxs.select('//script[contains(text(), "catalog_product_view_type_grouped")]')
        if sub_products:
            html = sub_products.re('jQuery\(.+\.html\(\"(.+)\"\);')[0]
            html = self.stripslashes(html)
            hxs_item = HtmlXPathSelector(text=html)
            
            sub_products = hxs_item.select('//table//tr[descendant::a]')
            for sub_product in sub_products:
                loader = ProductLoader(item=Product(), selector=sub_product)
                # \u00a3
                price = sub_product.select('.//span[@class="price"]/text()').extract()[0].strip()
                price = price.replace("u00a3","")
                loader.add_value('name', name + ' ' + "\u20AC" + price)
                loader.add_value('url', response.url)
                loader.add_value('price', price)
                loader.add_value('sku', sub_product.re('Code: (\w+)')[0])
                yield loader.load_item()
            
        
    def stripslashes(self, s):
        r = re.sub(r"\\(n|r)", "\n", s)
        r = re.sub(r"\\", "", r)
        return r
