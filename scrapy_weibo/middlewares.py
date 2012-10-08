import urllib2
import redis
import simplejson as json
import time
from scrapy import log
from scrapy.exceptions import CloseSpider
from scrapy.conf import settings
from scrapy_redis.req_count import ReqCount


# weibo apis default extras config
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
API_KEY = 'test'
LIMIT_URL = 'https://api.weibo.com/2/account/rate_limit_status.json?access_token={access_token}'


class RequestTokenMiddleware(object):
    req_count = None

    def __init__(self):
        host = settings.get("REDIS_HOST", REDIS_HOST)
        port = settings.get("REDIS_PORT", REDIS_PORT)
        api_key = settings.get("API_KEY", API_KEY)
        log.msg('Redis connect to {host}:{port}'.format(host=host, port=port), level=log.WARNING)
        r = redis.Redis(host, port)
        self.req_count = ReqCount(r, api_key)

        for token in self.req_count.all_tokens():
            _, remaining = self.get_limit_sts(token)
            self.req_count.reset(token, 1000 - remaining)

    def process_request(self, request, spider):
        token, used = self.req_count.one_token()

        if token is None:
            log.msg("No Token Available", level=log.WARNING)
            raise CloseSpider('')

        if used > 900:
            reset_time_in, remaining = self.get_limit_sts(token)
            if remaining < 100:
                log.msg("{spider} REACH API LIMIT, SLEEP {reset_time_in} SECONDS".format(
                    spider=spider.name, reset_time_in=reset_time_in), level=log.WARNING)
                time.sleep(reset_time_in)

            for token in self.req_count.all_tokens():
                _, remaining = self.get_limit_sts(token)
                self.req_count.reset(token, 1000 - remaining)

        log.msg("Token: {token}, used: {used}".format(token=token, used=used))
        request.headers['Authorization'] = 'OAuth2 %s' % token

    def get_limit_sts(self, token):
        retry = 0
        while 1:
            retry += 1
            if retry > 3:
                raise CloseSpider('CHECK LIMIT STATUS FAIL')

            try:
                time.sleep(1000)
                resp = urllib2.urlopen(LIMIT_URL.format(access_token=token))
                resp = json.loads(resp.read())
                reset_time_in = resp['reset_time_in_seconds']
                remaining = resp['remaining_user_hits']
                return reset_time_in, remaining
            except:
                pass
