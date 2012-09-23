import redis


def txt_to_redis(host, port, uids_set, tokens_set):
    r = redis.Redis(host, port)
    pipe = r.pipeline()
    pipe.multi()
    with open('uids.txt') as f:
        for line in f:
            pipe.sadd(uids_set, line.strip("\n"))
    pipe.execute()
    token = "2.00r8mVqCyoqaVE209c946192N8eKgD"
    r.sadd(tokens_set, token)

if __name__ == "__main__":
    host = 'localhost'
    port = 6379
    uids_set = "user_timeline:uids"
    tokens_set = "user_timeline:tokens"
    txt_to_redis(host, port, uids_set, tokens_set)
