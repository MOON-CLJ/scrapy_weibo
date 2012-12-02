#-*-coding:utf-8-*-
"""friends_spider"""

import redis
import simplejson as json
from scrapy.spider import BaseSpider
from utils4scrapy.utils import resp2item_v2
from utils4scrapy.tk_maintain import _default_redis, _default_req_count, _default_tk_alive, \
    EXPIRED_TOKEN, INVALID_ACCESS_TOKEN
from scrapy import log
from scrapy.conf import settings
from scrapy.exceptions import CloseSpider
from scrapy.http import Request
from utils4scrapy.utils import local2unix

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
UIDS_SET = '{spider}:uids_for_friends'
FRIENDS_URL = 'https://api.weibo.com/2/friendships/friends.json?uid={uid}&cursor={cursor}&count=200&trim_status=0'
SOURCE_USER_URL = 'https://api.weibo.com/2/users/show.json?uid={uid}'

class FriendSpider(BaseSpider):
    name = 'friends'
    r = None

    def start_requests(self):
        uid_seeds = self.prepare()

        for sid in uid_seeds:
            request = Request(SOURCE_USER_URL.format(uid=sid), headers=None,
                              callback=self.source_user)
            request.meta['retry'] = 0
            request.meta['sid'] = sid
            yield request

    def source_user(self, response):
        retry = response.meta['retry']
        sid = response.meta['sid']
        resp = json.loads(response.body)
        if response.status != 200:
            if resp.get('error_code') in [EXPIRED_TOKEN, INVALID_ACCESS_TOKEN]:
                token = response.request.headers['Authorization'][7:]
                _default_req_count(r=self.r).delete(token)
                _default_tk_alive(r=self.r).drop_tk(token)

                retry += 1
                if retry > 2:
                    return

                request = Request(SOURCE_USER_URL.format(uid=sid), headers=None,callback=self.source_user, dont_filter=True)

                request.meta['retry'] = retry
                request.meta['sid'] = sid
                yield request

                return
            else:
                raise CloseSpider(resp['error'])

	items = resp2item_v2(resp)
        if len(items) < 2:
	    retry += 1
	    if retry > 2:
	        return

	    request = Request(SOURCE_USER_URL.format(uid=sid), headers=None, callback=self.soucre_user, dont_filter=True)

	    request.meta['retry'] = retry
	    request.meta['sid'] = sid
	    yield request

	    return
        user = items[0]
        request = Request(FRIENDS_URL.format(uid=sid, cursor=0), headers=None, callback=self.friends)
        request.meta['retry'] = 0
        request.meta['sid'] = sid
        request.meta['cursor'] = 0
        request.meta['source_user'] = user
        yield request

        for item in items:
            yield item

    def friends(self, response):
        retry = response.meta['retry']
        sid = response.meta['sid']
        cursor = response.meta['cursor']
        source_user = response.meta['source_user']
        resp = json.loads(response.body)
        if response.status != 200:
            if resp.get('error_code') in [EXPIRED_TOKEN, INVALID_ACCESS_TOKEN]:
                token = response.request.headers['Authorization'][7:]
                _default_req_count(r=self.r).delete(token)
                _default_tk_alive(r=self.r).drop_tk(token)

                retry += 1
                if retry > 2:
                    return

                request = Request(FRIENDS_URL.format(uid=sid, cursor=cursor), headers=None,callback=self.friends, dont_filter=True)

                request.meta['retry'] = retry
                request.meta['sid'] = sid
                request.meta['cursor'] = cursor
                request.meta['source_user'] = source_user

                yield request
                return
            else:
                raise CloseSpider(resp['error'])

        for friend in resp['users']:
	    items = resp2item_v2(friend)
	    if items == []:
	        continue
	    user = items[0] #取出用户信息
	    source_user['friends'].append(int(user['id']))
	    for item in items:
    	        yield item
	
        next_cursor = resp['next_cursor']
        if next_cursor != 0:
            request = Request(FRIENDS_URL.format(uid=sid, cursor=next_cursor), headers=None, callback=self.friends, dont_filter=True)
            request.meta['retry'] = retry
            request.meta['sid'] = sid
            request.meta['cursor'] = next_cursor
            request.meta['source_user'] = source_user

            yield request
        else:
            yield source_user

    def prepare(self):
        host = settings.get("REDIS_HOST", REDIS_HOST)
        port = settings.get("REDIS_PORT", REDIS_PORT)
        uids_set = UIDS_SET.format(spider=self.name)

        self.r = redis.Redis(host, port)

        log.msg("load uids from {uids_set}".format(uids_set=uids_set), level=log.INFO)
        uids = self.r.smembers(uids_set)
        if len(uids) == 0:
            log.msg("{spider}: NO USER IDS TO LOAD".format(spider=self.name), level=log.WARNING)
        print uids
        return uids
