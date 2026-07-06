import uuid
from redisIface import RedisIface
from helper.jwt import token_required

@token_required
def getId():
    redis = RedisIface()
    id = str(uuid.uuid4())
    private_id = str(uuid.uuid4())
    try:
        redis.redis_hset(id, 'bot', 'false')
        redis.redis_hset(id, 'privateid', private_id)
        del redis
    except Exception as e:
        del redis
        # logger.critical("proxy Error while working getId with Redis: " + str(e))
        print("proxy Error while working getId with Redis: " + str(e))
    return {'id': id, 'privateid': private_id}