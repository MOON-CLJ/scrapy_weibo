import time
from scrapy_weibo.items import WeiboItem, UserItem
from scrapy.exceptions import DropItem


def resp2item(resp):
    """ /statuses/show  api structured data to item"""

    weibo = WeiboItem()
    user = UserItem()

    if 'deleted' in resp:
        raise DropItem('deleted')

    if 'reposts_count' not in resp:
        raise DropItem('reposts_count')

    weibo_keys = ['created_at', 'id', 'mid', 'text', 'source', 'reposts_count',
                  'comments_count', 'attitudes_count', 'geo']
    for k in weibo_keys:
        weibo[k] = resp[k]

    weibo['timestamp'] = local2unix(weibo['created_at'])

    user_keys = ['id', 'name', 'gender', 'province', 'city', 'location',
                 'description', 'verified', 'followers_count',
                 'statuses_count', 'friends_count', 'profile_image_url',
                 'bi_followers_count', 'verified', 'verified_reason']
    for k in user_keys:
        user[k] = resp['user'][k]

    weibo['user'] = user

    retweeted_user = None
    if 'retweeted_status' in resp and 'deleted' not in resp['retweeted_status']:
        retweeted_status = WeiboItem()
        retweeted_user = UserItem()

        for k in weibo_keys:
            retweeted_status[k] = resp['retweeted_status'][k]
        retweeted_status['timestamp'] = local2unix(retweeted_status['created_at'])

        for k in user_keys:
            retweeted_user[k] = resp['retweeted_status']['user'][k]

        retweeted_status['user'] = retweeted_user
        weibo['retweeted_status'] = retweeted_status

    return user, weibo, retweeted_user


def local2unix(time_str):
    time_format = '%a %b %d %H:%M:%S +0800 %Y'
    return time.mktime(time.strptime(time_str, time_format))
