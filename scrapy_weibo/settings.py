# Scrapy settings for scrapy_weibo project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'weibo'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['scrapy_weibo.spiders']
NEWSPIDER_MODULE = 'scrapy_weibo.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

# enables scheduling storing requests queue in redis
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# don't cleanup redis queues, allows to pause/resume crawls
SCHEDULER_PERSIST = False
SCHEDULER_REFRESH = True

DOWNLOAD_DELAY = 2

SPIDER_MIDDLEWARES = {
    'scrapy.contrib.spidermiddleware.offsite.OffsiteMiddleware': None,
    'scrapy.contrib.spidermiddleware.referer.RefererMiddleware': None,
    'scrapy.contrib.spidermiddleware.urllength.UrlLengthMiddleware': None,
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.robotstxt.RobotsTxtMiddleware': None,
    'scrapy.contrib.downloadermiddleware.httpauth.HttpAuthMiddleware': None,
    'scrapy_weibo.middlewares.RequestTokenMiddleware': 300,
    'scrapy.contrib.downloadermiddleware.defaultheaders.DefaultHeadersMiddleware': None,
}

ITEM_PIPELINES = [
    'scrapy_weibo.pipelines.MongodbPipeline',
]

#dev
"""
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
MONGOD_HOST = 'localhost'
MONGOD_PORT = 27017
"""

#prod

REDIS_HOST = '219.224.135.60'
REDIS_PORT = 6379
MONGOD_HOST = '219.224.135.60'
MONGOD_PORT = 27017
