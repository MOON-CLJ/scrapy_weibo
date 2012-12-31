# -*- coding: utf-8 -*-

from settings import *

# enables scheduling storing requests queue in redis
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# don't cleanup redis queues, allows to pause/resume crawls
SCHEDULER_PERSIST = True
SCHEDULER_REFRESH = True

DOWNLOAD_DELAY = 2

# retry 直接在downloader middlewares这一层处理
# 将400 403等有用的预知的错误留给spider middlewares处理
RETRY_HTTP_CODES = [500, 502, 503, 504, 408]

SPIDER_MIDDLEWARES = {
    'utils4scrapy.middlewares.ErrorRequestMiddleware': 40,
    'scrapy.contrib.spidermiddleware.offsite.OffsiteMiddleware': None,
    'scrapy.contrib.spidermiddleware.referer.RefererMiddleware': None,
    'scrapy.contrib.spidermiddleware.urllength.UrlLengthMiddleware': None,
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.robotstxt.RobotsTxtMiddleware': None,
    'scrapy.contrib.downloadermiddleware.httpauth.HttpAuthMiddleware': None,
    'utils4scrapy.middlewares.RequestTokenMiddleware': 310,
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'scrapy.contrib.downloadermiddleware.defaultheaders.DefaultHeadersMiddleware': None,
    'scrapy.contrib.downloadermiddleware.redirect.RedirectMiddleware': None,
    'scrapy.contrib.downloadermiddleware.cookies.CookiesMiddleware': None,
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': None,
}

ITEM_PIPELINES = [
    'utils4scrapy.pipelines.MongodbPipeline',
]

EXTENSIONS = {
    'scrapy.webservice.WebService': None,
    'scrapy.telnet.TelnetConsole': None,
}

#dev
"""
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
MONGOD_HOST = 'localhost'
MONGOD_PORT = 27017
API_KEY = '1966311272'
"""

#prod
REDIS_HOST = '219.224.135.60'
REDIS_PORT = 6379
MONGOD_HOST = '219.224.135.60'
MONGOD_PORT = 27017
API_KEY = '4131380600'
