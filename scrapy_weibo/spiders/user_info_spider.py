#-*-coding:utf-8-*-
"""spider for showing user personal information"""

import simplejson as json
from scrapy.spider import BaseSpider
from utils4scrapy.utils import resp2item_v2
from utils4scrapy.tk_maintain import _default_redis
from scrapy import log
from scrapy.conf import settings
from scrapy.http import Request


REDIS_HOST = 'localhost'
REDIS_PORT = 6379
API_KEY = '4131380600'
UIDS_SET = '{spider}:uids'
BASE_URL = 'https://api.weibo.com/2/users/show.json?uid={uid}'


class UserSpider(BaseSpider):
    name = 'user_info'

    def start_requests(self):
        uids = self.prepare()

        for uid in uids:
            request = Request(BASE_URL.format(uid=uid), headers=None)
            yield request

    def parse(self, response):
        resp = json.loads(response.body)

        items = resp2item_v2(resp)
        return items

    def prepare(self):
        host = settings.get('REDIS_HOST', REDIS_HOST)
        port = settings.get('REDIS_PORT', REDIS_PORT)
        self.r = _default_redis(host, port)

        uids_set = UIDS_SET.format(spider=self.name)
        log.msg(format='Load uids from %(uids_set)s', level=log.WARNING, uids_set=uids_set)
        uids = self.r.smembers(uids_set)
        if uids == []:
            log.msg(format='Not load any uids from %(uids_set)s', level=log.WARNING, uids_set=uids_set)

        return uids
