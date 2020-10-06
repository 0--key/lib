from scrapy.contrib.spiders import CSVFeedSpider

from product_spiders.items import Product, ProductLoader


class HouseoffraserCoUkSpider(CSVFeedSpider):
    name = 'houseoffraser.co.uk'
    allowed_domains = ['localhost']
    start_urls = (
        'http://localhost/tec7products.csv',
        )

    delimiter = ','
    headers = ['description', 'url', 'our ref', 'retail']

    def parse_row(self, response, row):
        if row['url'] == 'url':
            return []

        name = row['description']
        url = row['url']

        price = row['retail']

        l = ProductLoader(item=Product(), response=response)
        l.add_value('name', name)
        l.add_value('identifier', url)
        l.add_value('url', url)
        l.add_value('price', price)
        return l.load_item()
