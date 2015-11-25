# Scrapy settings for guns project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'guns'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['guns.spiders']
NEWSPIDER_MODULE = 'guns.spiders'
DEFAULT_ITEM_CLASS = 'guns.items.GunsItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

