# -*- coding: utf-8 -*-

from scrapy.item import Item, Field


class UserItem(Item):
    id = Field()
    name = Field()
    gender = Field()
    province = Field()
    city = Field()
    location = Field()
    description = Field()
    verified = Field()
    verified_reason = Field()
    followers_count = Field()  # 粉丝数
    statuses_count = Field()
    friends_count = Field()  # 关注数
    profile_image_url = Field()
    bi_followers_count = Field()  # 互粉数
    followers = Field()  # just ids
    friends = Field()  # just ids

    active = Field()
    first_in = Field()
    last_modify = Field()

    def __init__(self, *args, **kwargs):
        self._values = {}
        # set default
        default_keys = ['followers', 'friends']
        for key in default_keys:
            self._values[key] = []
        if args or kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).iteritems():
                self[k] = v

    def to_dict(self):
        d = {}
        for k, v in self.items():
            if type(v) in [UserItem, WeiboItem]:
                d[k] = v.to_dict()
            else:
                d[k] = v
        return d


class WeiboItem(Item):
    created_at = Field()
    timestamp = Field()
    id = Field()
    mid = Field()
    text = Field()
    source = Field()
    reposts_count = Field()
    comments_count = Field()
    attitudes_count = Field()
    bmiddle_pic = Field()
    original_pic = Field()
    geo = Field()
    urls = Field()
    hashtags = Field()
    emotions = Field()
    at_users = Field()
    repost_users = Field()
    user = Field()
    retweeted_status = Field()
    reposts = Field()  # just ids
    comments = Field()  # just ids

    first_in = Field()
    last_modify = Field()

    def __init__(self, *args, **kwargs):
        self._values = {}
        # set default
        default_keys = ['reposts', 'comments']
        for key in default_keys:
            self._values[key] = []

        if args or kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).iteritems():
                self[k] = v

    def to_dict(self):
        d = {}
        for k, v in self.items():
            if type(v) in [UserItem, WeiboItem]:
                d[k] = v.to_dict()
            else:
                d[k] = v

            """
            elif type(v) == list:
                d[k] = []
                for vv in v:
                    d[k].append(vv.to_dict())
            else:
                d[k] = v
            """

        return d
