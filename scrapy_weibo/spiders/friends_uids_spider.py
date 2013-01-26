#-*-coding:utf-8-*-
"""friends_uids_spider"""

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
UIDS_SET = '{spider}:uids_for_friends'
FRIENDS_URL = 'https://api.weibo.com/2/friendships/friends/ids.json?uid={uid}&cursor={cursor}&count=5000'
SOURCE_USER_URL = 'https://api.weibo.com/2/users/show.json?uid={uid}'


class FriendsUidSpider(BaseSpider):
    name = 'friends_uids'

    def start_requests(self):
        uids = self.prepare()

        for uid in uids:
            request = Request(SOURCE_USER_URL.format(uid=uid), headers=None,
                              callback=self.source_user)
            request.meta['uid'] = uid
            yield request

    def source_user(self, response):
        uid = response.meta['uid']
        resp = json.loads(response.body)
        results = []

        items = resp2item_v2(resp)
        if len(items) < 2:
            raise ShouldNotEmptyError()
        results.extend(items)

        user = items[0]
        request = Request(FRIENDS_URL.format(uid=uid, cursor=0), headers=None,
                          callback=self.more_friends)
        request.meta['uid'] = uid
        request.meta['cursor'] = 0
        request.meta['source_user'] = user
        results.append(request)

        return results

    def more_friends(self, response):
        uid = response.meta['uid']
        source_user = response.meta['source_user']

        resp = json.loads(response.body)
        results = []

        source_user['friends'].extend(resp['ids'])

        next_cursor = resp['next_cursor']
        if next_cursor != 0:
            request = Request(FRIENDS_URL.format(uid=uid, cursor=next_cursor), headers=None,
                              callback=self.more_friends)
            request.meta['uid'] = uid
            request.meta['source_user'] = source_user
            results.append(request)
        else:
            results.append(source_user)

        return results

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
