import redis
import os
import sys


def txt_to_redis(host, port, uids_set):
    r = redis.Redis(host, port)
    r.delete(uids_set)
    """
    # set
    pipe = r.pipeline()
    pipe.multi()
    with open('weibo_mid_list.txt') as f:
        for line in f:
            print line.split()[0]
            pipe.sadd(uids_set, line.split()[0])
    pipe.execute()
    """

    # sorted set
    pipe = r.pipeline()
    pipe.multi()
    count = 0
    with open('uids_for_friends_20130414.txt') as f:
        for line in f:
            if count >= 10000 and count <100000:
                print line.split()[0]
                pipe.sadd(uids_set, line.split()[0])
            count += 1
    pipe.execute()

    """
    pipe.multi()
    with open('token_list.txt') as f:
        for line in f:
            print line.split()[0]
            pipe.zadd(tokens_set, line.split()[0], 0)
    pipe.execute()
    """

if __name__ == "__main__":
    #host = 'localhost'
    host = '219.224.135.60'
    port = 6379
    #uids_set = "repost_timeline:weiboids"
    #uids_set = "user_timeline_april:uids"
    uids_set = "friends_uids:uids_for_friends"
    #uids_set = "user_info:uids"
    #uids_set = "user_timeline:uids"
    #uids_set = "friends_uids:uids_for_friends"
    #uids_set = "followers_uids:uids_for_followers"
    txt_to_redis(host, port, uids_set)
