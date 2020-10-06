try:
    import json
except ImportError:
    import simplejson as json

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from product_spiders.items import Product, ProductLoader

import logging


class SkypeEnZaSpider(BaseSpider):
    store_ids = {
            '17699',
            '17712',
            '17675',
            '17705',
            '17676',
            '17651',
            '17700',
            '17710',
            '17722',
            '17659',
            '17643',
            '17642',
            '17718',
            '17638',
            '17644',
            '17702',
            '17649',
            '17641',
            '17666',
            '17648',
            '17645',
            '17679',
            '17653',
            '17715',
            '17664',
            '17671',
            '17711',
            '17656',
            '17662',
            '17672',
            '17669',
            '17650',
            '17707',
            '17663',
            '17719',
            '17701',
            '17721',
            '17657',
            '17640',
            '17668',
            '29665'
        }

    products = [
        "/headsets/mini-jack/iss-talk-8120-freetalk-handsfree/",
        "/headsets/usb/iss-talk-5115-everyman/",
        "/headsets/usb/iss-talk-5204-freetalk-mono/",
        "/headsets/wireless/iss-talk-5195-everyman-wireless/",
        "/headsets/wireless/iss-talk-5192-freetalk/",
        "/phones/cordless-router/rtx-dualphone-4088-black/",
        "/phones/cordless-router/rtx-dualphone-4088-white/",
        "/phones/plug-in/iss-talk-3000-freetalk-office-phone/",
        "/phones/speakerphones/clear-chat-60/",
        "/phones/speakerphones/clear-chat-160/",
        "/phones/speakerphones/yamaha-projectphone-psg-01s/",
        "/webcams/hd-capable/iss-talk-7140/",
        "/webcams/hd-capable/fv-touchcam-n1/",
        "/webcams/hd-capable/iss-talk-7182-freetalk-conference-hd-camera/",
        "/webcams/standard-quality/iss-talk-7002/",
        "/webcams/tvwebcams/iss-talk-7182/",
        ]

    name = 'SkypeEnZa'
    allowed_domains = ['skype.com']
    start_urls = ()

    site_name = 'http://shop.skype.com/intl/en-za'

    ajax_url = "http://shop.skype.com/proxy/proxy.php?productid=%%prod_id%%&shopid=%%shop_id%%"

    def start_requests(self):
        for product in self.products:
            url  = self.site_name + product
            yield Request(url, self.parse)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        name = hxs.select("//div[@class='prodMain']/h1/text()").extract()
        if not name:
            logging.error("NO NAME! %s" % response.url)
            return
        name = name[0].strip()

        items = hxs.select("//span[@class='buy_now_compare']")
        i = 0
        for item in items:
            prod_id = item.select("@prodid").extract()[0]
            shop_id = item.select("@shopid").extract()[0]
            if shop_id in self.store_ids:
                url = self.ajax_url.replace("%%prod_id%%", prod_id).replace("%%shop_id%%", shop_id)

                yield Request(url, callback=self.parse_ajax, meta={'name': name, 'url': response.url})
                i += 1
                logging.error("Processing product %s" % i)


    def parse_ajax(self, response):
        content = response.body.strip("()")
        result = json.loads(content)[0]

        price = result['Promotion']

        if price:
            name = response.meta['name']
            url = response.meta['url']

            product = Product()
            loader = ProductLoader(item=product, response=response)
            loader.add_value('url', url)
            loader.add_value('name', name)
            loader.add_value('price', price)

            yield loader.load_item()
        else:
            logging.error("No price %s" % response.meta['url'])