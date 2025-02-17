import flask
from redis.exceptions import RedisError
from logger import logger
from redisIface import RedisIface

def onDisconnection(id):
    redis = RedisIface()
    try:
        # Check if id is valid
        id = redis.check_id(id)
        if id == None:
            del redis
            logger.critical("proxy onDisconnection id error")
            return {}
        redis.redis_hset(id, 'connected', 'false')
        # self.nb_conn -= 1
        del redis
        return {}
    except RedisError as e:
        del redis
        logger.critical("proxy onDisconnection error redis: " + str(e))
        return {}
    except Exception as e:
        del redis
        logger.critical("proxy onDisconnection args error: " + str(e))