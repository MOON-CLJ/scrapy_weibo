# -*- coding: utf-8 -*-

import math
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
WEIBOIDS_SET = '{spider}:weiboids'
BASE_URL = 'https://api.weibo.com/2/statuses/repost_timeline.json?id={id}&page={page}&count=200'
SOURCE_WEIBO_URL = 'https://api.weibo.com/2/statuses/show.json?id={id}'


class RepostTimelineSpider(BaseSpider):
    name = 'repost_timeline'
    r = None
    handle_httpstatus_list = [403]

    def start_requests(self):
        wids = self.prepare()

        for wid in wids:
            request = Request(SOURCE_WEIBO_URL.format(id=wid), headers=None,
                              callback=self.soucre_weibo)
            request.meta['retry'] = 0
            request.meta['wid'] = wid

            yield request

    def soucre_weibo(self, response):
        retry = response.meta['retry']
        wid = response.meta['wid']
        resp = json.loads(response.body)
        if response.status != 200:
            if resp.get('error_code') in [EXPIRED_TOKEN, INVALID_ACCESS_TOKEN]:
                token = response.request.headers['Authorization'][7:]
                self.req_count.delete(token)
                self.tk_alive.drop_tk(token)

                retry += 1
                if retry > 2:
                    return

                request = Request(SOURCE_WEIBO_URL.format(id=wid), headers=None,
                                  callback=self.soucre_weibo, dont_filter=True)

                request.meta['retry'] = retry
                request.meta['wid'] = wid
                yield request

                return
            else:
                raise CloseSpider(resp['error'])

        items = resp2item_v2(resp)
        if len(items) < 2:
            retry += 1
            if retry > 2:
                return

            request = Request(SOURCE_WEIBO_URL.format(id=wid), headers=None,
                              callback=self.soucre_weibo, dont_filter=True)

            request.meta['retry'] = retry
            request.meta['wid'] = wid
            yield request

            return

        for item in items:
            yield item

        weibo = items[0]
        reposts_count = weibo['reposts_count']
        wid = weibo['id']
        for i in range(1, int(math.ceil(reposts_count / 200.0)) + 1):
            request = Request(BASE_URL.format(id=wid, page=i), headers=None,
                              callback=self.more_reposts)

            request.meta['page'] = i
            request.meta['retry'] = 0
            request.meta['wid'] = wid
            request.meta['source_weibo'] = weibo

            yield request

    def more_reposts(self, response):
        resp = json.loads(response.body)
        page = response.meta['page']
        retry = response.meta['retry']
        wid = response.meta['wid']
        source_weibo = response.meta['source_weibo']

        if response.status != 200 and resp.get('error_code') in [EXPIRED_TOKEN, INVALID_ACCESS_TOKEN] \
                or 'reposts' not in resp or resp['reposts'] == []:

            if response.status != 200 and resp.get('error_code') in [EXPIRED_TOKEN, INVALID_ACCESS_TOKEN]:
                token = response.request.headers['Authorization'][7:]
                self.req_count.delete(token)
                self.tk_alive.drop_tk(token)

            retry += 1
            if retry > 2:
                return
            request = Request(BASE_URL.format(id=wid, page=page), headers=None,
                              callback=self.more_reposts, dont_filter=True)

            request.meta['page'] = page
            request.meta['retry'] = retry
            request.meta['wid'] = wid
            request.meta['source_weibo'] = source_weibo

            yield request
            return
        elif response.status != 200:
            raise CloseSpider(resp['error'])

        for repost in resp['reposts']:
            items = resp2item_v2(repost)
            if items == []:
                continue
            weibo = items[0]  # 取出转发微博
            source_weibo['reposts'].append(weibo['id'])
            for item in items:
                yield item

        yield source_weibo

    def prepare(self):
        host = settings.get("REDIS_HOST", REDIS_HOST)
        port = settings.get("REDIS_PORT", REDIS_PORT)
        api_key = settings.get("API_KEY", API_KEY)
        self.r = _default_redis(host, port)
        self.req_count = _default_req_count(r=self.r, api_key=api_key)
        self.tk_alive = _default_tk_alive(r=self.r, api_key=api_key)

        weiboids_set = WEIBOIDS_SET.format(spider=self.name)
        log.msg('load weiboids from {weiboids_set}'.format(weiboids_set=weiboids_set), level=log.INFO)
        weiboids = self.r.smembers(weiboids_set)
        if weiboids == []:
            log.msg('{spider}: NO WEIBO IDS TO LOAD'.format(spider=self.name), level=log.WARNING)

        return weiboids
