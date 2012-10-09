import pymongo
import time
from scrapy.conf import settings
from scrapy import log
from scrapy_weibo.items import WeiboItem, UserItem


MONGOD_HOST = 'localhost'
MONGOD_PORT = 27017


class MongodbPipeline(object):
    """
    insert and update items to mongod
    """

    def __init__(self):
        host = settings.get("MONGOD_HOST", MONGOD_HOST)
        port = settings.get("MONGOD_PORT", MONGOD_PORT)
        connection = pymongo.Connection(host, port)
        db = connection.admin
        db.authenticate('root', 'root')
        log.msg('Mongod connect to {host}:{port}'.format(host=host, port=port), level=log.WARNING)

        db = connection.master_timeline
        self.db = db

    def process_item(self, item, spider):
        if isinstance(item, WeiboItem):
            self.process_weibo(item)
        elif isinstance(item, UserItem):
            self.process_user(item)

        return item

    def process_weibo(self, item):
        weibo = item.to_dict()
        weibo['_id'] = weibo['id']

        if self.db.master_timeline_weibo.find({'_id': weibo['_id']}).count():
            old_weibo = self.db.master_timeline_weibo.find_one(
                {'_id': weibo['_id']})

            update_keys = ['reposts_count', 'comments_count', 'attitudes_count']
            updates = {}

            flag = False
            for more_repost in weibo['reposts']:
                if more_repost not in old_weibo['reposts']:
                    old_weibo['reposts'].append(more_repost)
                    flag = True
            if flag:
                updates['reposts'] = old_weibo['reposts']

            updates['last_modify'] = time.time()
            # comments should update
            for key in update_keys:
                if key in weibo and weibo[key] is not None \
                        and (key not in old_weibo or weibo[key] != old_weibo[key]):
                    updates[key] = weibo[key]

            self.db.master_timeline_weibo.update({'_id': weibo['_id']},
                                                 {"$set": updates})
        else:
            weibo['first_in'] = time.time()
            weibo['last_modify'] = weibo['first_in']
            self.db.master_timeline_weibo.insert(weibo)

    def process_user(self, item):
        user = item.to_dict()
        user['_id'] = user['id']
        if self.db.master_timeline_user.find({'_id': user['_id']}).count():
            old_user = self.db.master_timeline_user.find_one(
                {'_id': user['_id']})

            update_keys = ['name', 'gender', 'province', 'city',
                           'location', 'description', 'verified', 'followers_count',
                           'statuses_count', 'friends_count', 'profile_image_url',
                           'bi_followers_count', 'verified', 'verified_reason']
            updates = {}

            flag = False
            for more_follower in user['followers']:
                if more_follower not in old_user['followers']:
                    old_user['followers'].append(more_follower)
                    flag = True
            if flag:
                updates['followers'] = old_user['followers']

            flag = False
            for more_friend in user['friends']:
                if more_friend not in old_user['friends']:
                    old_user['friends'].append(more_friend)
                    flag = True
            if flag:
                updates['friends'] = old_user['friends']

            updates['last_modify'] = time.time()

            for key in update_keys:
                if key in user and user[key] is not None \
                        and (key not in old_user or user[key] != old_user[key]):
                    updates[key] = user[key]

            self.db.master_timeline_user.update({'_id': user['_id']},
                                                {"$set": updates})

        else:
            user['first_in'] = time.time()
            user['last_modify'] = user['first_in']
            user['active'] = False  # default
            self.db.master_timeline_user.insert(user)
