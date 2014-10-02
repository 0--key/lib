from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest

from product_spiders.items import Product, ProductLoader

try:
    import json
except ImportError:
    import simplejson as json

json_api_url = "http://www.flashingsdirect.com/remote.php"
json_api_request_args = {
    'action': 'add',
    'currency_id': '',
    'product_id': '',
    'qty[]': '',
    'variation_id': '',
    'w': 'getProductAttributeDetails'
}


class FlashingsdirectSpider(BaseSpider):
    name = "flashingsdirect"
    allowed_domains = ["flashingsdirect.com"]
    start_urls = (
            'http://www.flashingsdirect.com/categories/Pipe-Flashings/All-Pipe-Flashings/Standard-Square-Base/',
            'http://www.flashingsdirect.com/categories/Pipe-Flashings/All-Pipe-Flashings/Universal-Round-Base/',
            'http://www.flashingsdirect.com/retrofit-square-base/',
            'http://www.flashingsdirect.com/categories/Pipe-Flashings/All-Pipe-Flashings/Universal-Round-Base-Retrofit/'
        )

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        items = hxs.select("//div[@id='CategoryContent']//ul/li")
        for item in items:
            for url in item.select("div[@class='ProductDetails']/strong/a/@href").extract():
                yield Request(url, callback=self.parse_item)

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)
        items = hxs.select("//div[@id='ProductDetails']/div[@class='BlockContent']")
        for item in items:
            title = item.select("h2/text()").extract()[0]
            url = response.url
            product_id = item.select(
                "div[@class='ProductMain']/div[@class='productAddToCartRight']/\
                 form[@id='productDetailsAddToCartForm']/input[@name='product_id']/@value").extract()[0]
            select_el = item.select(
                "div[@class='ProductMain']/div[@class='productAddToCartRight']/\
                 form[@id='productDetailsAddToCartForm']/div[@class='ProductDetailsGrid ProductAddToCart']/\
                 div[@class='productAttributeList']/div/\
                 div[@class='productAttributeValue']/div[@class='productOptionViewSelect']/select")
            field_name = select_el.select("@name").extract()[0]
            options = select_el.select('option')
            for option in options:
                option_name = option.select("text()").extract()[0]
                option_value = option.select("@value").extract()[0]
                if not option_value:
                    continue
                item_options = json_api_request_args.copy()
                item_options[field_name] = option_value
                item_options['product_id'] = product_id

                new_item_name = title + " " + option_name
                request = FormRequest(
                    url=json_api_url,
                    formdata=item_options,
                    callback=self._parse_item_json
                )
                request.meta['item_name'] = new_item_name
                request.meta['item_url'] = url
                request.meta['subtype_id'] = option_value
                yield request

    def _parse_item_json(self, response):
        item_name = response.request.meta['item_name']
        item_url = response.request.meta['item_url']
        # subtype_id = response.request.meta['subtype_id']

        data = json.loads(response.body)
        price = data['details']['unformattedPrice']

        l = ProductLoader(item=Product(), response=response)
        l.add_value('identifier', str(item_name))
        l.add_value('name', item_name)
        l.add_value('url', item_url)
        l.add_value('price', price)
        return l.load_item()
