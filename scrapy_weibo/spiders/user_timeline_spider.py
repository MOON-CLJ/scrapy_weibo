# -*- coding: utf-8 -*-

import simplejson as json
import sys
import time
from scrapy.spider import BaseSpider
from utils4scrapy.utils import resp2item_v2
from utils4scrapy.tk_maintain import _default_redis
from utils4scrapy.middlewares import ShouldNotEmptyError
from scrapy import log
from scrapy.conf import settings
from scrapy.http import Request

try:
    import pydablooms
except ImportError:
    from utils4scrapy.tk_maintain import _default_mongo

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
MONGOD_HOST = 'localhost'
MONGOD_PORT = 27017
API_KEY = '4131380600'
UIDS_SET = '{spider}:uids'
# redis hash ie: HGET user_timeline:uids_with_priority {uid}
# 0 <= score <= 10 [0, 3] [4, 7] [8, 10]
UIDS_PRIORITY_SET = '{spider}:uids_with_priority'
DEFAULT_SCORE = 5
AT_LEAST_UPDATE_COUNT = 50
DABLOOMS_CAPACITY = 2000000000
DABLOOMS_ERROR_RATE = .00001
DABLOOMS_FILEPATH = '%s/bloom.bin' % settings.get('PROJECT_ROOT', '/tmp')
BASE_URL = 'https://api.weibo.com/2/statuses/user_timeline.json?uid={uid}&page={page}&count=100'


class UserTimelineSpider(BaseSpider):
    """usage: scrapy crawl user_timeline -a gt=4 -a lt=7"""
    name = 'user_timeline'

    def __init__(self, gt, lt):
        self.gt = int(gt)
        self.lt = int(lt)
        if 'pydablooms' in sys.modules.keys():
            self.bloom = pydablooms.Dablooms(capacity=DABLOOMS_CAPACITY,
                                             error_rate=DABLOOMS_ERROR_RATE, filepath=DABLOOMS_FILEPATH)
        else:
            self.bloom = None
            host = settings.get('MONGOD_HOST', MONGOD_HOST)
            port = settings.get('MONGOD_PORT', MONGOD_PORT)
            self.db = _default_mongo(host, port, usedb='master_timeline')

    def start_requests(self):
        uids = self.prepare()

        for uid in uids:
            request = Request(BASE_URL.format(uid=uid, page=1), headers=None)

            request.meta['page'] = 1
            request.meta['uid'] = uid
            yield request

    def parse(self, response):
        page = response.meta['page']
        uid = response.meta['uid']

        resp = json.loads(response.body)
        results = []

        if resp.get('statuses') == []:
            raise ShouldNotEmptyError()

        for status in resp['statuses']:
            items = resp2item_v2(status)
            results.extend(items)

        # filter or mongo, 检查是否有大于70个有效更新，有则翻页，如果是page=1 还得做积分反馈
        update_count = 0
        if self.bloom:
            for status in resp['statuses']:
                if 'mid' in status and not self.bloom.check(status['mid']):
                    update_count += 1
                    # 更新到filter
                    self.bloom.add(status['mid'], int(time.time() * 1000))
        else:
            for status in resp['statuses']:
                if 'id' in status and self.db.master_timeline_weibo.find({'_id': status['id']}).limit(1).count() == 0:
                    update_count += 1

        if page == 1:
            if update_count > 0 and self.r.hget(self.uids_priority_set, uid) < 10:
                self.r.hincrby(self.uids_priority_set, uid, 1)
            elif update_count == 0 and self.r.hget(self.uids_priority_set, uid) > 0:
                self.r.hincrby(self.uids_priority_set, uid, -1)

        if update_count > AT_LEAST_UPDATE_COUNT:
            page += 1
            request = Request(BASE_URL.format(uid=uid, page=page), headers=None)
            request.meta['page'] = page
            request.meta['uid'] = uid

            results.append(request)

        return results

    def prepare(self):
        host = settings.get('REDIS_HOST', REDIS_HOST)
        port = settings.get('REDIS_PORT', REDIS_PORT)
        self.r = _default_redis(host, port)

        uids_set = UIDS_SET.format(spider=self.name)
        uids_priority_set = UIDS_PRIORITY_SET.format(spider=self.name)
        self.uids_priority_set = uids_priority_set

        log.msg(format='Load uids from %(uids_set)s', level=log.WARNING, uids_set=uids_set)
        uids = self.r.smembers(uids_set)
        if uids == []:
            log.msg(format='Not load any uids from %(uids_set)s', level=log.WARNING, uids_set=uids_set)

        # 初始化priority
        for uid in uids:
            if not self.r.hexists(self.uids_priority_set, uid):
                self.r.hset(self.uids_priority_set, uid, DEFAULT_SCORE)

        # 根据priority过滤uids
        uids = [uid for uid in uids if self.gt <= int(self.r.hget(self.uids_priority_set, uid)) <= self.lt]
        log.msg(format='%(length)s uids between %(gt)s -> %(lt)s will be process', level=log.INFO, length=len(uids), gt=self.gt, lt=self.lt, uids_set=uids_set)
        return uids
