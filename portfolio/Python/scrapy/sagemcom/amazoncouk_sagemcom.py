__author__ = 'juraseg'

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoader

import logging


class AmazonCoUkSagemcomSpider(BaseSpider):
    name = 'amazon.co.uk_sagemcom'
    allowed_domains = ['amazon.co.uk']
    start_urls = (
        'http://amazon.co.uk/',
        )
    search_url = 'http://www.amazon.co.uk/s?ie=UTF8&search-type=ss&index=electronics-uk&field-keywords='

    products = [
                'http://www.amazon.co.uk/Humax-HDR-FOX-T2-Recorder-Freeview/dp/B004BMB2XC/ref=sr_1_1?ie=UTF8&qid=1332751153&sr=8-1',
                'http://www.amazon.co.uk/Humax-HDR-FOX-T2-Freeview-1TB/dp/B004NEKNEM/ref=sr_1_1?s=electronics&ie=UTF8&qid=1332752781&sr=1-1',
                'http://www.amazon.co.uk/Humax-500GB-Satellite-Receiver-Recorder/dp/B0039J42LM/ref=sr_1_2?ie=UTF8&qid=1332751153&sr=8-2',
                'http://www.amazon.co.uk/Panasonic-DMR-HW100EBK-Recorder-Freeview-Tuners/dp/B005GCXUZE/ref=sr_1_1?ie=UTF8&qid=1332752320&sr=8-1',
                'http://www.amazon.co.uk/Samsung-SMT-S7800-500GB-Freesat-Recorder/dp/B004S5ZUJ4/ref=sr_1_1?s=electronics&ie=UTF8&qid=1332752573&sr=1-1',
                'http://www.amazon.co.uk/Sagemcom-RTI90-320-T2-HD-Recorder/dp/B003EIKYDS/ref=sr_1_11?ie=UTF8&qid=1335175589&sr=8-11',
                'http://www.amazon.co.uk/Humax-PVR9300T-320GB-Digital-Recorder/dp/B00272N9PC/ref=sr_1_3?s=electronics&ie=UTF8&qid=1335177591&sr=1-3',
                'http://www.amazon.co.uk/Sony-SVRHDT500B-Freeview-Personal-Recorder/dp/B004MPR0V6/ref=sr_1_1?s=electronics&ie=UTF8&qid=1335178705&sr=1-1',
                'http://www.amazon.co.uk/Philips-PicoPIX-PX2055-Business-Projector/dp/B006U1F9OK/ref=sr_1_1?ie=UTF8&qid=1338808349&sr=8-1',
                'http://www.amazon.co.uk/Philips-Pico-PPX1230-Projector-Lumens/dp/B0042F2PE8/ref=sr_1_1?ie=UTF8&qid=1338372683&sr=8-1',
                'http://www.amazon.co.uk/Philips-PPX1430-Multimedia-Pocket-Projector/dp/B0042F56AS',
                'http://www.amazon.co.uk/Philips-Pico-PPX1020-Projector-Lumens/dp/B0042F5662',
                'http://www.amazon.co.uk/s/?ie=UTF8&keywords=amazon&tag=googhydr-21&index=aps&hvadid=10152339886&hvpos=1t1&hvexid=&hvnetw=g&hvrand=946855828277962979&hvpone=&hvptwo=&hvqmt=b&ref=pd_sl_75kd1j0l62_b',
                'http://www.amazon.co.uk/Pico-Genie-A100-iPhone-Touch/dp/B006GQRVEK',
                'http://www.amazon.co.uk/3M-MP160-Pocket-Projector/dp/B00452V1ZW',
                'http://www.amazon.com/3M-MPRO150-MPro150-Pocket-Projector/dp/B0031ESJ78',
                'http://www.amazon.co.uk/3m-MP180-Pico-Portable-Projector/dp/B004BLIN1W',
                'http://www.amazon.co.uk/3M-MPRO120-Pocket-Mini-Projector/dp/B002K8Y2HC/ref=sr_1_1?ie=UTF8&qid=1338376354&sr=8-1',
                'http://www.amazon.co.uk/3M-MP220-Mobile-Pocket-Projector/dp/B007NU3QOM',
                'http://www.amazon.co.uk/Optoma-PK301-Pico-Pocket-Projector/dp/B003U690U2',
                'http://www.amazon.co.uk/Optoma-Pico-Pocket-PK120-Projector/dp/B005F5CJQS',
                'http://www.amazon.co.uk/Optoma-PK-320-Pico-Projector-WVGA/dp/B005UXRS48/ref=sr_1_1?ie=UTF8&qid=1338377015&sr=8-1',
                'http://www.amazon.co.uk/Optoma-OPTOMAPK201-LED-Pocket-Projector/dp/B003H0TYWK/ref=sr_1_1?s=electronics&ie=UTF8&qid=1338377138&sr=1-1',
                'http://www.amazon.com/Microvision-SHOWWX-Laser-Projector-AA0123600-020/dp/B005D6D6DY',
                'http://www.amazon.co.uk/Microvision-SHOWWX-Laser-Pico-Projector/dp/B003G5ML9Y/ref=sr_1_1?ie=UTF8&qid=1338377619&sr=8-1',
                'http://www.amazon.co.uk/Acer-C110-DLP-Projector-2000/dp/B00551DPIS',
                'http://www.amazon.co.uk/Acer-C112-Ultra-Portable-Projector/dp/B004QH7UQK',

    ]

    keywords = ['Sagemcom']

    def start_requests(self):
        for keyword in self.keywords:
            url = self.search_url + keyword
            yield Request(url, callback=self.parse_search)

        for url in self.products:
            yield Request(url, callback=self.parse_product)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)

        url = response.url

        name = hxs.select(
            "//form[@id='handleBuy']/div[@class='buying']/h1[@class='parseasinTitle']/span/text()").extract()
        if not name:
            logging.error("ERROR! NO NAME! %s" % url)
            return
        name = name[0]

        price = hxs.select("//div[@id='priceBlock']//tr[@id='actualPriceRow']//b[@class='priceLarge']/text()").extract()
        if not price:
            logging.error("ERROR! NO PRICE! %s %s" % (url, name))
            return
        price = price[0]

        description = u''

        l = ProductLoader(item=Product(), response=response)
        l.add_value('identifier', name)
        l.add_value('name', name)
        l.add_value('url', url)
        l.add_value('price', price)
        yield l.load_item()

    def parse_search(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        # parse products
        items = hxs.select("//div[@id='rightResultsATF']/div/div[contains(@class, 'results')]/div/div[@class='data']")
        for item in items:
            name = item.select("h3[@class='title']/a/text()").extract()
            if not name:
                logging.error("ERROR! NAME! URL: %s." % response.url)
                continue
            name = name[0]

            url = item.select("h3[@class='title']/a/@href").extract()
            if not url:
                logging.error("ERROR! NOT FOUND URL! URL: %s. NAME: %s" % (response.url, name))
                continue
            url = url[0]
            url = urljoin_rfc(base_url, url)
            price = item.select("div[@class='newPrice']/span[contains(@class, 'price')]/text()").extract()
            if not price:
                logging.warning("No new products, only used. URL: %s. NAME: %s" % (response.url, name))
                continue
            price = price[0]

            l = ProductLoader(item=Product(), response=response)
            l.add_value('identifier', name)
            l.add_value('name', name)
            l.add_value('url', url)
            l.add_value('price', price)
            yield l.load_item()

        items2 = hxs.select(
            "//div[@id='rightResultsATF']/div/div[@id='atfResults' or @id='btfResults']/div/div[contains(@class, 'result')]")
        for item in items2:
            name = item.select("div[@class='productTitle']/a/text()").extract()
            if not name:
                logging.error("ERROR! NAME! URL: %s." % response.url)
                continue
            name = name[0]

            url = item.select("div[@class='productTitle']/a/@href").extract()
            if not url:
                logging.error("ERROR! NOT FOUND URL! URL: %s. NAME: %s" % (response.url, name))
                continue
            url = url[0]
            url = urljoin_rfc(base_url, url)
            price = item.select("div/div[@class='newPrice']/span/text()").extract()
            if not price:
                logging.warning("No new products, only used. URL: %s. NAME: %s" % (response.url, name))
                continue
            price = price[0]

            l = ProductLoader(item=Product(), response=response)
            l.add_value('identifier', name)
            l.add_value('name', name)
            l.add_value('url', url)
            l.add_value('price', price)
            yield l.load_item()

        # parse pages
        if len(items) > 0 or len(items2) > 0:
            # process next page
            page_param_index = response.url.find("page=")
            if page_param_index > -1:
                # page > 1
                page_param_index += len("page=")
                current_page = int(response.url[page_param_index:])
                next_page_url = response.url[:page_param_index] + str(current_page + 1)
            else:
                next_page_url = response.url + "&page=" + str(2)
            request = Request(next_page_url, callback=self.parse_search)
            yield request
