import pymongo
import re
from scrapy.conf import settings
from scrapy import log


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

        db = connection.weibo
        self.db = db

    def process_item(self, item, spider):
        weibo = {}
        weibo['_id'] = item['id']
        weibo['uid'] = item['user']['uid']
        weibo['created_at'] = item['created_at']
        weibo['txt_len'] = len(item['text'])
        weibo['source'] = item['source']
        weibo['comments_count'] = item['comments_count']

        text = item['text']
        weibo['text'] = text
        weibo['at_users'] = re.findall(r' @(\S+)', text)

        if 'retweeted_status' in item:
            weibo['is_retweet'] = True
            repost_users = re.findall(r'//@(\S+?):', text)
            sweibo_username = item['retweeted_status']['user']['name']
            if len(repost_users) > 0:
                weibo['link'] = [repost_users[0], sweibo_username]
            else:
                weibo['link'] = [sweibo_username] * 2
        else:
            weibo['is_retweet'] = False

        self.db.april_weibo.save(weibo)

        user = {}
        user['uid'] = item['user']['uid']
        user['_id'] = user['uid']
        user['name'] = item['user']['name']
        user['location'] = item['user']['location']
        user['gender'] = item['user']['gender']
        user['verified'] = item['user']['verified']
        self.db.april_user.save(user)

        return item
