# -*- coding: utf-8 -*-

from settings import *

# enables scheduling storing requests queue in redis
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# don't cleanup redis queues, allows to pause/resume crawls
SCHEDULER_PERSIST = True
SCHEDULER_REFRESH = True

DOWNLOAD_DELAY = 2

# middlewares 的意思是在engine和download handler之间有一层，包括进入download
# handler之前和从download handler出来之后，同理spider (handler)
# retry 直接在downloader middlewares这一层处理
# 将400 403等有用的预知的错误留给spider middlewares处理
RETRY_HTTP_CODES = [500, 502, 503, 504, 408]

SPIDER_MIDDLEWARES = {
    'utils4scrapy.middlewares.ErrorRequestMiddleware': 40,
    'scrapy.contrib.spidermiddleware.offsite.OffsiteMiddleware': None,
    'scrapy.contrib.spidermiddleware.referer.RefererMiddleware': None,
    'scrapy.contrib.spidermiddleware.urllength.UrlLengthMiddleware': None,
    'utils4scrapy.middlewares.SentrySpiderMiddleware': 1000,
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
    'utils4scrapy.middlewares.SentryDownloaderMiddleware': 1000,
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
SENTRY_DSN = 'http://e1b6b5f0d81e497799c667c1634eca22:facc62aa2c5c44c1a620bc33be8bb6d7@0.0.0.0:9000/2'
"""

#prod
REDIS_HOST = '219.224.135.60'
REDIS_PORT = 6379
MONGOD_HOST = '219.224.135.60'
MONGOD_PORT = 27017
API_KEY = '4131380600'
SENTRY_DSN = 'http://3349196dad314183ba8e07edcd95b884:feb54ca50ead45d2bef6e6571cf76229@219.224.135.60:9000/2'
