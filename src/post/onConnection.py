from redis.exceptions import RedisError
from logger import logger
from helper.jwt import token_required
from core.redis_client import redis_client as r

@token_required
def onConnection(current_user):
    try:
        r.hset(f"user:{current_user.id}", 'connected', 'true')
        # self.nb_conn += 1
        return {"status":"success"}, 200
    except RedisError as e:
        logger.critical("proxy onConn error redis: " + str(e))
        return {"status":"error"}, 500
    except Exception as e:
        logger.critical("proxy onConn args error: " + str(e))
        return {"status":"error"}, 500