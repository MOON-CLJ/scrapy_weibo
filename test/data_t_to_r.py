import redis


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
    with open('random_users.txt') as f:
        for line in f:
            print line.split()[0]
            pipe.sadd(uids_set, line.split()[0])
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
    #uids_set = "friends:uids_for_friends"
    uids_set = "user_timeline_april:uids"
    #uids_set = "user_timeline:uids"
    #uids_set = "friends_uids:uids_for_friends"
    txt_to_redis(host, port, uids_set)
