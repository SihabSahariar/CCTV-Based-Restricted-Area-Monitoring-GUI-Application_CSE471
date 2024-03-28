import redis
r = redis.Redis()

def stream():
    stream_keys = r.keys("*")
    return stream_keys

def dstream():
    stream_keys = r.keys("*")
    for key in stream_keys:
        r.delete(key)
    stream_keys = r.keys("*")
    return stream_keys
