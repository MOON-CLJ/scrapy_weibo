# -*- coding: utf-8 -*-

from utils4scrapy.items import WeiboItem, UserItem
from utils4scrapy.pipelines import MongodbPipeline
import simplejson as json

FILEPATH = '/home/mirage/Downloads/data/items2.jl'

pipe = MongodbPipeline()

with open(FILEPATH, 'r') as f:
    user_count = 0
    weibo_count = 0
    for line in f.readlines():
        resp = json.loads(line)
        item = None
        if 'mid' in resp:
            weibo = WeiboItem()
            for key in resp.keys():
                weibo[key] = resp[key]
            item = weibo
            weibo_count += 1
        else:
            user = UserItem()
            for key in resp.keys():
                user[key] = resp[key]
            item = user
            user_count += 1

        if item:
            pipe.process_item(item, None)
            print '.'

        print 'weibo:', weibo_count, 'user:', user_count
