import flask
from redis.exceptions import RedisError
from logger import logger
from redisIface import RedisIface
import datetime

def onConnection(id):
    redis = RedisIface()
    try:
        # Check if id is valid
        id = redis.check_id(id)
        if id == None:
            del redis
            logger.critical("proxy onConnection id error")
            return {}
        print(datetime.date.today())
        redis.redis_hset(id, 'lastConn', str(datetime.date.today()))
        redis.redis_hset(id, 'connected', 'true')
        del redis
        return {}
    except RedisError as e:
        del redis
        logger.critical("proxy onConn error redis: " + str(e))
        return {}
    except Exception as e:
        del redis
        logger.critical("proxy onConn args error: " + str(e))
