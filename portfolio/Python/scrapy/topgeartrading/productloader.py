import HTMLParser

from scrapy.contrib.loader.processor import MapCompose

from product_spiders.items import ProductLoader, Product

def remove_entities(s):
    parser = HTMLParser.HTMLParser()
    res = s.strip()
    return parser.unescape(res)

class WindowsCleaningProductLoader(ProductLoader):
    name_in = MapCompose(unicode, remove_entities)


def load_product(product, response):
    p = Product()
    loader = WindowsCleaningProductLoader(item=p, response=response)
    loader.add_value('url', product['url'])
    loader.add_value('name', product['description'])
    loader.add_value('price', product['price'])
    loader.add_value('sku', product.get('sku', ''))

    return loader.load_item()
