# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class KrakItem(Item):
    # define the fields for your item here like:
    # name = Field()
    # pass#
    company_name = Field()
    company_site_url = Field()
    short_description = Field()
    address = Field()
    phone = Field()
    phone_type = Field()
    gen_description = Field()
    description_headers = Field()
    description_paragraphs = Field()
    tags = Field()
    category = Field()
    
