# -*- coding: utf-8 -*-

import os

SPIDER_MODULES = ['scrapy_weibo.spiders']
NEWSPIDER_MODULE = 'scrapy_weibo.spiders'
BOT_NAME = 'weibo'


# enables scheduling storing requests queue in redis
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# don't cleanup redis queues, allows to pause/resume crawls
SCHEDULER_PERSIST = True

DOWNLOAD_DELAY = 2

# middlewares 的意思是在engine和download handler之间有一层，包括进入download
# handler之前和从download handler出来之后，同理spider (handler)
# retry 直接在downloader middlewares这一层处理
# 将400 403等有用的预知的错误留给spider middlewares处理

# ** ** ** ** ** ** ** ** ** **
# downloadermiddleware 1 process_request
# ** ** ** ** ** ** ** ** ** **
# downloadermiddleware 2 process_request
# ** ** ** ** ** ** ** ** ** **
# downloadermiddleware 2 process_response
# ** ** ** ** ** ** ** ** ** **
# downloadermiddleware 1 process_response
# ** ** ** ** ** ** ** ** ** **
# spidermiddleware 1 process_spider_input
# ** ** ** ** ** ** ** ** ** **
# spidermiddleware 2 process_spider_input
# spider parse
# ** ** ** ** ** ** ** ** ** **
# spidermiddleware 2 process_spider_output
# ** ** ** ** ** ** ** ** ** **
# spidermiddleware 1 process_spider_output

RETRY_HTTP_CODES = [500, 502, 503, 504, 408]

SPIDER_MIDDLEWARES = {
    'utils4scrapy.middlewares.ErrorRequestMiddleware': 40,
    'scrapy.contrib.spidermiddleware.offsite.OffsiteMiddleware': None,
    'scrapy.contrib.spidermiddleware.referer.RefererMiddleware': None,
    'scrapy.contrib.spidermiddleware.urllength.UrlLengthMiddleware': None,
    'scrapy.contrib.spidermiddleware.depth.DepthMiddleware': None,
    # 如果process_spider_input或spider里抛出错误，
    # process_spider_exception是反向执行的，即要想记录错误得先过sentry，在捕获重试
    'utils4scrapy.middlewares.RetryErrorResponseMiddleware': 940,
    #'utils4scrapy.middlewares.SentrySpiderMiddleware': 950,
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
    #'utils4scrapy.middlewares.SentryDownloaderMiddleware': 950,
}

ITEM_PIPELINES = [
    'utils4scrapy.pipelines.MongodbPipeline',
    'scrapy_weibo.pipelines.JsonWriterPipeline',
]

EXTENSIONS = {
    'scrapy.webservice.WebService': None,
    'scrapy.telnet.TelnetConsole': None,
}

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

IS_PROD = 1

if IS_PROD:
    #prod
    REDIS_HOST = '219.224.135.60'
    REDIS_PORT = 6379
    MONGOD_HOST = '219.224.135.60'
    MONGOD_PORT = 27017
    API_KEY = '4131380600'
    SENTRY_DSN = 'http://f67703ce57604e249a7de5d687b8d914:1c8f9a8d1daf4a8fb18445beac098dd1@219.224.135.60:9000/2'
else:
    #dev
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    MONGOD_HOST = 'localhost'
    MONGOD_PORT = 27017
    API_KEY = '1966311272'
    SENTRY_DSN = 'http://e1b6b5f0d81e497799c667c1634eca22:facc62aa2c5c44c1a620bc33be8bb6d7@0.0.0.0:9000/2'
