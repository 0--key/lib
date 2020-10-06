# scrapy includes
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

# spider includes
from product_spiders.items import Product, ProductLoader

# main class
class AllegroMedicalSpider(BaseSpider):

    # setup
    name = "allegromedical.com" # Name must match the domain
    allowed_domains = ["allegromedical.com"]
    start_urls = ["http://www.allegromedical.com/categorysitemap.html",]

    # main request
    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        # extract subcategories
        subCategoryUrls = hxs.select("//table[@class='subcategories']//a/@href").extract()

        # iterate category urls
        for subCategoryUrl in subCategoryUrls:
            yield Request(urljoin_rfc(base_url, subCategoryUrl))

        nextPageLink = hxs.select("//img[@alt='NEXT']")

        # if there is a next page...
        if nextPageLink:
            yield Request(urljoin_rfc(base_url, nextPageLink.select("../@href")[0].extract()))

        # iterate products
        # for product in self.parse_products(hxs, base_url):
        #    yield product

        productUrls = hxs.select("//div[@class='category']/div[@class='cat-inside']/a/@href").extract()
        for productUrl in productUrls:
            yield Request(urljoin_rfc(base_url, productUrl), callback=self.parse_product)

    def parse_product(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        main_name = hxs.select('//span[@id="mainProductName"]/text()').extract()[0].strip()
        main_price = hxs.select("//dd[@class='price']/text()").extract()[0]
        dec = hxs.select("//dd[@class='price']/span/text()").extract()
        if dec:
            main_price += dec[0]

        skus = []
        sku_text = hxs.select("//strong[text()='Mfg Part Number(s):']/../text()").extract()
        if sku_text:
            skus += [sku.strip() for sku in sku_text[0].split(', ')]

        sub_products = hxs.select('//select[@id="skuIdSelection"]/option')
        if sub_products:
            for p in sub_products:
                p_parts = p.select('.//text()').extract()[0].split('-')
                if p_parts[-1].strip().startswith('$'):
                    price = p_parts[-1].strip()
                else:
                    price = main_price

                sku_id = p.select('.//@value').extract()[0]
                sub_product_node = hxs.select('//input[@name="skuId" and @value="%s"]/../div' % sku_id)
                sku = None
                if sub_product_node:
                    sku = self._get_sku(sub_product_node.select('.//text()').extract()[0], skus)

                loader = ProductLoader(item=Product(), response=response)
                loader.add_value('url', response.url)
                loader.add_value('name', main_name + ' ' + ''.join(p_parts[:-1]).strip())
                loader.add_value('price', price)
                if sku:
                    loader.add_value('sku', sku)

                yield loader.load_item()
        else:
            loader = ProductLoader(item=Product(), response=response)
            loader.add_value('url', response.url)
            loader.add_value('name', main_name)
            loader.add_value('price', main_price)
            if skus:
                loader.add_value('sku', skus[0].strip())
            yield loader.load_item()

    def _get_sku(self, product_text, skus):
        result_sku = ''
        for sku in skus:
            if product_text.lower().strip().startswith(sku.lower()):
                if len(sku) > len(result_sku):
                    result_sku = sku

        return result_sku or None