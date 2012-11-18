import time
from scrapy import log
from scrapy.conf import settings
from utils4scrapy.tk_maintain import token_status, one_valid_token, \
    _default_redis, _default_req_count, _default_tk_alive, \
    HOURS_LIMIT, EXPIRED_TOKEN, INVALID_ACCESS_TOKEN


# weibo apis default extras config
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
API_KEY = '4131380600'
BUFFER_SIZE = 100


class RequestTokenMiddleware(object):
    def __init__(self):
        api_key = settings.get("API_KEY", API_KEY)
        self.api_key = api_key

        host = settings.get("REDIS_HOST", REDIS_HOST)
        port = settings.get("REDIS_PORT", REDIS_PORT)
        log.msg('[Request token middleware] Redis connect to {host}:{port}'.format(host=host, port=port), level=log.WARNING)
        self.r = _default_redis(host, port)

        self.req_count = _default_req_count(self.r, self.api_key)
        self.tk_alive = _default_tk_alive(self.r, self.api_key)

    def process_request(self, request, spider):
        token, used = one_valid_token(self.req_count, self.tk_alive)

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
