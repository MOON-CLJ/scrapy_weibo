BOT_NAME = 'weibo'
BOT_VERSION = '1.0'

DOWNLOAD_DELAY = 2

SPIDER_MODULES = ['scrapy_weibo.spiders']
NEWSPIDER_MODULE = 'scrapy_weibo.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)
