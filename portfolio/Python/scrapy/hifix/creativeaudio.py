import re
import os

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

import csv

from product_spiders.items import Product, ProductLoader


class CreativeAudioSpider(BaseSpider):
    name = 'creative-audio.co.uk'
    allowed_domains = ['www.creative-audio.co.uk']
    start_urls = ('http://www.creative-audio.co.uk/',)

    def __init__(self, *args, **kwargs):
        super(CreativeAudioSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # categories
        categories = hxs.select(u'//div[@class="menuItem"]/@onclick').re('\.assign\(\'(.*)\'')
        for url in categories:
            url = urljoin_rfc(get_base_url(response), '/' + url)
            if ('javascript' not in url) and ('Javascript' not in url):
                yield Request(url)

        # pages
        # next_pages = hxs.select(u'').extract()
        # for next_page in next_pages:
            # url = urljoin_rfc(get_base_url(response), next_page)
            # yield Request(url)

        # products
        products = hxs.select(u'//div/img/../@onclick').re('assign\(\'(.*)\'')
        products += hxs.select(u'//div[@class="catpadding"]//div[@class="DefaultFont"]/a/@href').extract()
        products += hxs.select(u'//table[@id="Table_01"]//div/a[child::img]/@href').extract()
        
        for url in products:
            url = urljoin_rfc(get_base_url(response), url)
            if ('javascript' not in url) and ('Javascript' not in url):
                yield Request(url, callback=self.parse_product)

        for product in self.parse_product(response):
            yield product


    def parse_product(self, response):
        if 'TERMS' in response.url or 'ABOUTUS' in response.url:
            return
        if not isinstance(response, HtmlResponse):
            return

        hxs = HtmlXPathSelector(response)

        products = hxs.select(u'//td[@class="linkcell"]/div[@onclick]/@onclick | //div[@id="DARKSTRIP"]//td[@onclick]/@onclick').re('assign\(\'(.*)\'')
        products += hxs.select(u'//div[@id="DARKSTRIP"]//a/@href').extract()
        products += hxs.select(u'//a["HDlistTitlefont"]/@href').extract()
        for url in set(products):
            url = urljoin_rfc(get_base_url(response), '/' + url)
            if ('javascript' not in url) and ('Javascript' not in url):
                yield Request(url, callback=self.parse_product)

        product_loader = ProductLoader(item=Product(), response=response)

        name = hxs.select(u'//title/text()').extract()[0]
        name = re.sub('\n', ' ', name)
        product_loader.add_value('name', name)
        product_loader.add_value('url', response.url)
        product_loader.add_xpath('price', u'//div[@class="HDPriceHD"]//span/text()', re='\xa3(.*)')
        product_loader.add_xpath('price', u'//div[@id="MASTER"]//td[@valign]/text()', re='\xa3(.*)')
        product_loader.add_xpath('price', u'//div[@class="HDPriceRRP"]//text()', re='.*?\xa3(.*)')
        if product_loader.get_output_value('price'):
            yield product_loader.load_item()

        products = hxs.select(u'//td[@class="DefaultFont"]')
        for product in products:
            name = product.select(u'.//p/strong/text()').extract()
            price = product.select(u'.//p/text()').re('\xa3(.*)\)')
            url = product.select(u'.//a[child::u]/@href').extract()
            if url:
                url = urljoin_rfc(get_base_url(response), '/' + url[0])
            if not price:
                continue
            product_loader = ProductLoader(item=Product(), selector=product)
            product_loader.add_value('name', name)
            product_loader.add_value('price', price)
            product_loader.add_value('url', url if url else response.url)
            yield product_loader.load_item()

        products = hxs.select(u'//td[@id="LIGHTSTRIP"]')
        for product in products:
            name = product.select(u'.//a[@class="DefaultFont" and contains(@style,"#000000")]/text()').extract()
            if len(name) > 1:
                name = map(lambda x: x.strip(), name)
                name = ' '.join(name)
            else:
                name = name[0].strip()
            price = product.select(u'.//span[contains(text(),"Hot Deal - only")]/span/text()').re('\xa3(.*)')
            if not price:
                price = product.select(u'.//span[@class="DefaultFont" and contains(text(),"RRP")]/text()').re('\xa3(.*)')
            if not price:
                continue
            url = product.select(u'.//a[@class="DefaultFont"]/@href').extract()
            if url:
                url = urljoin_rfc(get_base_url(response), '/' + url[0])
            product_loader = ProductLoader(item=Product(), selector=product)
            product_loader.add_value('name', name)
            product_loader.add_value('price', price)
            product_loader.add_value('url', url if url else response.url)
            yield product_loader.load_item()