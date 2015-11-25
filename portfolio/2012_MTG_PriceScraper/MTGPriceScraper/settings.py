# Scrapy settings for MTGPriceScraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'MTGPriceScraper'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['MTGPriceScraper.spiders']
NEWSPIDER_MODULE = 'MTGPriceScraper.spiders'
DEFAULT_ITEM_CLASS = 'MTGPriceScraper.items.MtgpricescraperItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

