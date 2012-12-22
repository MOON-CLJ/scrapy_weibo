# -*- coding: utf-8 -*-

import simplejson as json
from scrapy.spider import BaseSpider
from utils4scrapy.utils import resp2item_v2
from utils4scrapy.tk_maintain import _default_redis, _default_req_count, _default_tk_alive, \
    EXPIRED_TOKEN, INVALID_ACCESS_TOKEN
from scrapy import log
from scrapy.conf import settings
from scrapy.exceptions import CloseSpider
from scrapy.http import Request


REDIS_HOST = 'localhost'
REDIS_PORT = 6379
API_KEY = '4131380600'
UIDS_SET = '{spider}:uids'
BASE_URL = 'https://api.weibo.com/2/statuses/user_timeline.json?uid={uid}&page={page}&since_id={since_id}&max_id={max_id}&count=100'


class UserTimelineApril(BaseSpider):
    name = "user_timeline_april"
    r = None
    since_id = 3513504881782892
    max_id = 3523483302151071

    def start_requests(self):
        uids = self.prepare()

        for uid in uids:
            request = Request(BASE_URL.format(uid=uid, page=1,
                              since_id=self.since_id, max_id=self.max_id), headers=None,
                              callback=self.parse_next)

            request.meta['page'] = 1
            request.meta['retry'] = 0
            request.meta['uid'] = uid
            yield request

    def parse_next(self, response):
        page = response.meta['page']
        retry = response.meta['retry']
        uid = response.meta['uid']

        resp = json.loads(response.body)
        if response.status != 200:
            if resp.get('error_code') in [EXPIRED_TOKEN, INVALID_ACCESS_TOKEN]:
                token = response.request.headers['Authorization'][7:]
                self.req_count.delete(token)
                self.tk_alive.drop_tk(token)

                retry += 1
                if retry > 2:
                    return

                request = Request(BASE_URL.format(uid=uid, page=page,
                                  since_id=self.since_id, max_id=self.max_id), headers=None,
                                  callback=self.parse_next, dont_filter=True)

                request.meta['page'] = page
                request.meta['retry'] = retry
                request.meta['uid'] = uid
                yield request

                return
            else:
                raise CloseSpider(resp['error'])
        else:
            if resp.get('statuses') == []:
                return
            for status in resp['statuses']:
                items = resp2item_v2(status)
                if items == []:
                    continue
                for item in items:
                    yield item

            page += 1
            retry = 0

            request = Request(BASE_URL.format(uid=uid, page=page,
                              since_id=self.since_id, max_id=self.max_id), headers=None,
                              callback=self.parse_next, dont_filter=True)

            request.meta['page'] = page
            request.meta['retry'] = retry
            request.meta['uid'] = uid
            yield request

    def prepare(self):
        host = settings.get("REDIS_HOST", REDIS_HOST)
        port = settings.get("REDIS_PORT", REDIS_PORT)
        api_key = settings.get("API_KEY", API_KEY)
        self.r = _default_redis(host, port)
        self.req_count = _default_req_count(r=self.r, api_key=api_key)
        self.tk_alive = _default_tk_alive(r=self.r, api_key=api_key)

        uids_set = UIDS_SET.format(spider=self.name)
        log.msg('load uids from {uids_set}'.format(uids_set=uids_set), level=log.INFO)
        uids = self.r.smembers(uids_set)
        if uids == []:
            log.msg('{spider}: NO USER IDS TO LOAD'.format(spider=self.name), level=log.WARNING)

        return uids
