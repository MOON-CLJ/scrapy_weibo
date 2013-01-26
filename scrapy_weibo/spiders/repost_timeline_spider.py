# -*- coding: utf-8 -*-

import math
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
API_KEY = '4131380600'
WEIBOIDS_SET = '{spider}:weiboids'
BASE_URL = 'https://api.weibo.com/2/statuses/repost_timeline.json?id={id}&page={page}&count=200'
SOURCE_WEIBO_URL = 'https://api.weibo.com/2/statuses/show.json?id={id}'


class RepostTimelineSpider(BaseSpider):
    name = 'repost_timeline'

    def start_requests(self):
        wids = self.prepare()

        for wid in wids:
            request = Request(SOURCE_WEIBO_URL.format(id=wid), headers=None,
                              callback=self.soucre_weibo)
            request.meta['wid'] = wid

            yield request

    def soucre_weibo(self, response):
        resp = json.loads(response.body)
        results = []

        items = resp2item_v2(resp)
        if len(items) < 2:
            raise ShouldNotEmptyError()
        results.extend(items)

        weibo = items[0]
        reposts_count = weibo['reposts_count']
        wid = weibo['id']
        for i in range(1, int(math.ceil(reposts_count / 200.0)) + 1):
            request = Request(BASE_URL.format(id=wid, page=i), headers=None,
                              callback=self.more_reposts)

            request.meta['page'] = i
            request.meta['wid'] = wid
            request.meta['source_weibo'] = weibo

            results.append(request)

        return results

    def more_reposts(self, response):
        source_weibo = response.meta['source_weibo']
        resp = json.loads(response.body)
        results = []

        if resp['reposts'] == []:
            raise ShouldNotEmptyError()

        for repost in resp['reposts']:
            items = resp2item_v2(repost)
            if items == []:
                continue
            weibo = items[0]  # 取出转发微博
            source_weibo['reposts'].append(weibo['id'])
            results.extend(items)

        results.append(source_weibo)
        return results

    def prepare(self):
        host = settings.get('REDIS_HOST', REDIS_HOST)
        port = settings.get('REDIS_PORT', REDIS_PORT)
        self.r = _default_redis(host, port)

        weiboids_set = WEIBOIDS_SET.format(spider=self.name)
        log.msg(format='Load weiboids from %(weiboids_set)s', level=log.WARNING, weiboids_set=weiboids_set)
        weiboids = self.r.smembers(weiboids_set)
        if weiboids == []:
            log.msg(format='Not load any weiboids from %(weiboids_set)s', level=log.WARNING, weiboids_set=weiboids_set)

        return weiboids
