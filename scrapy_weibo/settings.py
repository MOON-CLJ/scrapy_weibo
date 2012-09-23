# Scrapy settings for scrapy_weibo project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'scrapy_weibo'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['scrapy_weibo.spiders']
NEWSPIDER_MODULE = 'scrapy_weibo.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)
# enables scheduling storing requests queue in redis
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# don't cleanup redis queues, allows to pause/resume crawls
SCHEDULER_PERSIST = False

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
