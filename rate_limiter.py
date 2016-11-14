import redis
import time
import os

r = redis.StrictRedis.from_url(os.environ.get('REDIS_URL'), db=0)
rate_limit_period_seconds = 10 # use this to limit calls per minute, hour, day, etc
rate_limit_per_period = 2        # number of allowed calls per period

def rate_limit(a_function):

    def wrapper(*args, **kwargs):
        timestamp = int(time.time())
        key = timestamp // rate_limit_period_seconds
        # print "timestamp is {0}, key is {1}".format(timestamp, key)
        pipe = r.pipeline()
        pipe.incr(key)
        pipe.expire(key, 5 * rate_limit_period_seconds)
        count = pipe.execute()[0]

        if count <= rate_limit_per_period:
            print "Count was {0}, proceeding".format(count)
            return a_function(*args, **kwargs)
        else:
            print "Count was {0}, rate limiting".format(count)
            return None

    return wrapper
