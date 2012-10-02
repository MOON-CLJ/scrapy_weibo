import redis


def txt_to_redis(host, port, uids_set, tokens_set):
    r = redis.Redis(host, port)
    pipe = r.pipeline()
    pipe.multi()
    with open('uidlist.txt') as f:
        for line in f:
            print line.split()[0]
            pipe.sadd(uids_set, line.split()[0])
    pipe.execute()
    token = []
    token.append('2.00TMVxDCyoqaVEdf26698d1atob5XC')
    token.append('2.0064O3zByoqaVEf6ed046d81FI2NMB')
    token.append('2.00OGiDACyoqaVEcca2ee5fb2xlKTSC')
    token.append('2.00r8mVqCyoqaVE209c946192N8eKgD')

    for t in token:
        r.zadd(tokens_set, t, 0)

if __name__ == "__main__":
    host = '219.224.135.60'
    port = 6379
    uids_set = "user_timeline_april:uids"
    tokens_set = "tokens:count"
    txt_to_redis(host, port, uids_set, tokens_set)
