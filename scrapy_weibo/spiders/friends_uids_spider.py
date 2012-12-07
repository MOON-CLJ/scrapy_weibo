#-*-coding:utf-8-*-
"""friends_uids_spider"""

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
UIDS_SET = '{spider}:uids_for_friends'
FRIENDS_URL = 'https://api.weibo.com/2/friendships/friends/ids.json?uid={uid}&cursor={cursor}&count=5000'
SOURCE_USER_URL = 'https://api.weibo.com/2/users/show.json?uid={uid}'


class FriendsUidSpider(BaseSpider):
    name = 'friends_uids'
    r = None
    handle_httpstatus_list = [403]

    def start_requests(self):
        uids = self.prepare()

        for uid in uids:
            request = Request(SOURCE_USER_URL.format(uid=uid), headers=None,
                              callback=self.source_user)
            request.meta['retry'] = 0
            request.meta['uid'] = uid
            yield request

    def source_user(self, response):
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

                request = Request(SOURCE_USER_URL.format(uid=uid), headers=None,
                                  callback=self.source_user, dont_filter=True)

                request.meta['retry'] = retry
                request.meta['uid'] = uid
                yield request

                return
            else:
                raise CloseSpider(resp['error'])

        items = resp2item_v2(resp)
        if len(items) < 2:
            retry += 1
            if retry > 2:
                return

            request = Request(SOURCE_USER_URL.format(uid=uid), headers=None,
                              callback=self.soucre_user, dont_filter=True)

            request.meta['retry'] = retry
            request.meta['uid'] = uid
            yield request

            return

        user = items[0]
        request = Request(FRIENDS_URL.format(uid=uid, cursor=0), headers=None,
                          callback=self.more_friends)
        request.meta['retry'] = 0
        request.meta['uid'] = uid
        request.meta['cursor'] = 0
        request.meta['source_user'] = user
        yield request

        for item in items:
            yield item

    def more_friends(self, response):
        retry = response.meta['retry']
        uid = response.meta['uid']
        cursor = response.meta['cursor']
        source_user = response.meta['source_user']
        resp = json.loads(response.body)

        if response.status != 200:
            if resp.get('error_code') in [EXPIRED_TOKEN, INVALID_ACCESS_TOKEN]:
                token = response.request.headers['Authorization'][7:]
                self.req_count.delete(token)
                self.tk_alive.drop_tk(token)

                retry += 1
                if retry > 2:
                    return

                request = Request(FRIENDS_URL.format(uid=uid, cursor=cursor), headers=None,
                                  callback=self.more_friends, dont_filter=True)

                request.meta['retry'] = retry
                request.meta['uid'] = uid
                request.meta['cursor'] = cursor
                request.meta['source_user'] = source_user

                yield request
                return
            else:
                raise CloseSpider(resp['error'])

        for friend_id in resp['ids']:
            source_user['friends'].append(friend_id)

        next_cursor = resp['next_cursor']
        if next_cursor != 0:
            request = Request(FRIENDS_URL.format(uid=uid, cursor=next_cursor), headers=None,
                              callback=self.more_friends, dont_filter=True)
            request.meta['retry'] = 0
            request.meta['uid'] = uid
            request.meta['cursor'] = next_cursor
            request.meta['source_user'] = source_user

            yield request
        else:
            yield source_user

    def prepare(self):
        host = settings.get("REDIS_HOST", REDIS_HOST)
        port = settings.get("REDIS_PORT", REDIS_PORT)
        api_key = settings.get("API_KEY", API_KEY)
        self.r = _default_redis(host, port)
        self.req_count = _default_req_count(r=self.r, api_key=api_key)
        self.tk_alive = _default_tk_alive(r=self.r, api_key=api_key)

        uids_set = UIDS_SET.format(spider=self.name)
        log.msg("load uids from {uids_set}".format(uids_set=uids_set), level=log.INFO)
        uids = self.r.smembers(uids_set)
        if uids == []:
            log.msg("{spider}: NO USER IDS TO LOAD".format(spider=self.name), level=log.WARNING)

        return uids
