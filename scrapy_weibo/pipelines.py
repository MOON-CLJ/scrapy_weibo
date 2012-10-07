import pymongo
from scrapy.conf import settings
from scrapy import log
from scrapy_weibo.items import WeiboItem, UserItem


MONGOD_HOST = 'localhost'
MONGOD_PORT = 27017


class MongodbPipeline(object):
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
            weibo = item.to_dict()
            weibo['_id'] = weibo['id']

            if self.db.master_timeline_weibo.find({'_id': weibo['_id']}).count():
                reposts = self.db.master_timeline_weibo.find_one(
                    {'_id': weibo['_id']})['reposts']

                repost_ids = (repost['id'] for repost in reposts)

                for more_repost in weibo['reposts']:
                    if more_repost['id'] not in repost_ids:
                        reposts.append(more_repost)

                self.db.master_timeline_weibo.update({'_id': weibo['_id']},
                                                     {"$set": {"reposts": reposts}})
            else:
                self.db.master_timeline_weibo.insert(weibo)
        elif isinstance(item, UserItem):
            user = item.to_dict()
            user['_id'] = user['id']
            self.db.master_timeline_user.save(user)

        return item
