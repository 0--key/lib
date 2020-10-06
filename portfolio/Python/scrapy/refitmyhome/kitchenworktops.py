from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import ProductLoader, Product

class kitchenworktopsSpider(BaseSpider):

    name = "kitchen-worktops-plus"
    allowed_domains = ["www.kitchen-worktops-plus.co.uk"]
    start_urls = ['http://www.kitchen-worktops-plus.co.uk/index.html',]

    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        items = hxs.select('//ul[@id="nav"]//li/a/@href').extract()

        for item in items:
            yield Request(urljoin_rfc(base_url,item), callback=self.parse_items)


    def parse_items(self,response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
        product = hxs.select("//div[@class='product_price_block']")
        usual = 1
        if not product:
            product = hxs.select("//table[@id='product_grid']")
            usual = 0
        if product:
            top_name = hxs.select("//h1/text()").extract()[0]
            if usual:
                subname = hxs.select('//div[@class="content"]/h2/text()').extract()
                if subname: top_name += " " + subname[0]
            product_name = top_name
            url = response.url
            rows = product.select(".//tr")
            price = None
            name = None
            if rows:
                if usual:
                    i = 0
                    for row in rows:
                        columns = row.select(".//td")
                        if columns:
                            if len(columns) == 1:
                                title = columns[0].select(".//strong/text()").extract()
                                if not title:
                                    title = columns[0].select(".//h3/text()").extract()
                                if title:
                                    product_name = top_name + " - " + title[0]
                            if len(columns) == 3:
                                price = columns[1].select(".//text()").extract()
                                if price:
                                    name = product_name + " - " + columns[0].select("./text()").extract()[0]
                                    i += 1
                                    l = ProductLoader(item=Product(), response=response)
                                    l.add_value('name', name)
                                    l.add_value('url', url)
                                    l.add_value('price', price)
                                    yield l.load_item()
                else:
                    price = rows[0].select(".//td/text()").extract()
                    if price:
                        name = product_name
                        l = ProductLoader(item=Product(), response=response)
                        l.add_value('name', name)
                        l.add_value('url', url)
                        l.add_value('price', price)
                        yield l.load_item()

        pages = hxs.select("//div[@class='product_swatch']")
        if pages:
            for page in pages:
                url = page.select(".//a/@href")
                if url:
                    yield Request(urljoin_rfc(base_url,url.extract()[0]), callback=self.parse_items)

        pages = hxs.select("//div[@class='product_swatch_100']")
        if pages:
            for page in pages:
                url = page.select(".//a/@href")
                if url:
                    yield Request(urljoin_rfc(base_url,url.extract()[0]), callback=self.parse_items)

        pages = hxs.select("//div[@class='swatch_float_left_100']")
        if pages:
            for page in pages:
                url = page.select(".//a/@href")
                if url:
                    yield Request(urljoin_rfc(base_url,url.extract()[0]), callback=self.parse_items)

        pages = hxs.select("//div[@class='product_block_150']")
        if pages:
            for page in pages:
                url = page.select(".//a/@href")
                if url:
                    yield Request(urljoin_rfc(base_url,url.extract()[0]), callback=self.parse_items)
