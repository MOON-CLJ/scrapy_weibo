# -*- coding: utf-8 -*-

import simplejson as json
from scrapy.spider import BaseSpider
from utils4scrapy.utils import resp2item_v2
from utils4scrapy.tk_maintain import _default_redis
from utils4scrapy.middlewares import ShouldNotEmptyError
from scrapy import log
from scrapy.conf import settings
from scrapy.http import Request


REDIS_HOST = 'localhost'
REDIS_PORT = 6379
UIDS_SET = '{spider}:uids'
BASE_URL = 'https://api.weibo.com/2/statuses/user_timeline.json?uid={uid}&page={page}&since_id={since_id}&max_id={max_id}&count=100'


class UserTimelineApril(BaseSpider):
    """usage: scrapy crawl user_timeline_april -a since_id=3421438975589423 -a max_id=3438780670993204"""
    name = 'user_timeline_april'

    def __init__(self, since_id, max_id):
        self.since_id = int(since_id)
        self.max_id = int(max_id)

    def start_requests(self):
        uids = self.prepare()

        for uid in uids:
            request = Request(BASE_URL.format(uid=uid, page=1,
                              since_id=self.since_id, max_id=self.max_id), headers=None)

            request.meta['page'] = 1
            request.meta['uid'] = uid
            yield request

    def parse(self, response):
        page = response.meta['page']
        uid = response.meta['uid']

        resp = json.loads(response.body)
        results = []

        if not resp.get('statuses'):
            raise ShouldNotEmptyError()

        for status in resp['statuses']:
            items = resp2item_v2(status)
            results.extend(items)

        page += 1
        request = Request(BASE_URL.format(uid=uid, page=page,
                          since_id=self.since_id, max_id=self.max_id), headers=None)
        request.meta['page'] = page
        request.meta['uid'] = uid

        results.append(request)

        return results

    def prepare(self):
        host = settings.get('REDIS_HOST', REDIS_HOST)
        port = settings.get('REDIS_PORT', REDIS_PORT)
        self.r = _default_redis(host, port)

        uids_set = UIDS_SET.format(spider=self.name)
        log.msg(format='Load uids from %(uids_set)s', level=log.INFO, uids_set=uids_set)
        uids = self.r.smembers(uids_set)
        if uids == []:
            log.msg(format='Not load any uids from %(uids_set)s', level=log.INFO, uids_set=uids_set)

        return uids
