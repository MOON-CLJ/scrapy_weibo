from settings import *

"""
Add token:
mannual add one more tokens
redis> ZADD tokens:count 0 {token}
redis> zrange tokens:count 0 -1 WITHSCORES

Add uids:
test/data_t_to_r.py
"""

# enables scheduling storing requests queue in redis
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# don't cleanup redis queues, allows to pause/resume crawls
SCHEDULER_PERSIST = True
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
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
MONGOD_HOST = 'localhost'
MONGOD_PORT = 27017
API_KEY = "4131380600"

#prod
"""
REDIS_HOST = '219.224.135.60'
REDIS_PORT = 6379
MONGOD_HOST = '219.224.135.60'
MONGOD_PORT = 27017
API_KEY = "4131380600"
"""
