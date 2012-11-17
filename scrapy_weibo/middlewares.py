import redis
import pymongo
import time
from scrapy import log
from scrapy.conf import settings
from utils4scrapy.req_count import ReqCount
from utils4scrapy.tk_alive import TkAlive
from utils4scrapy.tk_maintain import token_status, one_valid_token, \
    HOURS_LIMIT, EXPIRED_TOKEN, INVALID_ACCESS_TOKEN


# weibo apis default extras config
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
MONGOD_HOST = 'localhost'
MONGOD_PORT = 27017
API_KEY = 'test'
BUFFER_SIZE = 100


class RequestTokenMiddleware(object):
    def __init__(self):
        host = settings.get("REDIS_HOST", REDIS_HOST)
        port = settings.get("REDIS_PORT", REDIS_PORT)
        api_key = settings.get("API_KEY", API_KEY)
        self.api_key = api_key
        log.msg('[Request token middleware] Redis connect to {host}:{port}'.format(host=host, port=port), level=log.WARNING)
        r = redis.Redis(host, port)
        self.r = r

        host = settings.get("MONGOD_HOST", MONGOD_HOST)
        port = settings.get("MONGOD_PORT", MONGOD_PORT)
        connection = pymongo.Connection(host, port)
        db = connection.admin
        db.authenticate('root', 'root')
        log.msg('Mongod connect to {host}:{port}'.format(host=host, port=port), level=log.WARNING)

        db = connection.simple
        self.db = db

        self.req_count = ReqCount(r, api_key)
        self.tk_alive = TkAlive(r, api_key)

    def process_request(self, request, spider):
        token, used = one_valid_token(self.req_count, self.tk_alive)
        print token, used

        if used > HOURS_LIMIT - BUFFER_SIZE:
            while 1:
                tk_status = token_status(token)
                if tk_status in [EXPIRED_TOKEN, INVALID_ACCESS_TOKEN]:
                    self.req_count.delete(token)
                    self.tk_alive.drop_tk(token)
                    token, used = one_valid_token(self.req_count, self.tk_alive)
                else:
                    break

            reset_time_in, remaining = tk_status
            if remaining < BUFFER_SIZE:
                log.msg("{spider} REACH API LIMIT, SLEEP {reset_time_in} SECONDS".format(
                    spider=spider.name, reset_time_in=reset_time_in), level=log.WARNING)
                time.sleep(reset_time_in)

        log.msg("Token: {token}, used: {used}".format(token=token, used=used))
        request.headers['Authorization'] = 'OAuth2 %s' % token
