#-*-coding:utf-8-*-
"""spider for showing information of single status"""

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
MIDS_SET = '{spider}:mids'
BASE_URL = 'https://api.weibo.com/2/statuses/show.json?id={mid}'


class StatusesSpider(BaseSpider):
    name = 'statuses_show'

    def start_requests(self):
        mids = self.prepare()

        for mid in mids:
            request = Request(BASE_URL.format(mid=mid), headers=None)
            yield request

    def parse(self, response):
        resp = json.loads(response.body)

        items = resp2item_v2(resp)
        return items

    def prepare(self):
        host = settings.get('REDIS_HOST', REDIS_HOST)
        port = settings.get('REDIS_PORT', REDIS_PORT)
        self.r = _default_redis(host, port)

        mids_set = MIDS_SET.format(spider=self.name)
        log.msg(format='Load mids from %(mids_set)s', level=log.INFO, mids_set=mids_set)
        mids = self.r.smembers(mids_set)
        if mids == []:
            log.msg(format='Not load any mids from %(mids_set)s', level=log.INFO, mids_set=mids_set)

        return mids
