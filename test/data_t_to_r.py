import redis


def txt_to_redis(host, port, uids_set, tokens_set):
    r = redis.Redis(host, port)

    pipe = r.pipeline()
    pipe.multi()
    with open('weibo_mid_list.txt') as f:
        for line in f:
            print line.split()[0]
            pipe.sadd(uids_set, line.split()[0])
    pipe.execute()

    pipe.multi()
    with open('token_list.txt') as f:
        for line in f:
            print line.split()[0]
            pipe.zadd(tokens_set, line.split()[0], 0)
    pipe.execute()


if __name__ == "__main__":
    host = 'localhost'
    port = 6379
    uids_set = "repost_timeline:weiboids"
    tokens_set = "4131380600:tokens"
    txt_to_redis(host, port, uids_set, tokens_set)
