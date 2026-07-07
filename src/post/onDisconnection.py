from redis.exceptions import RedisError
from logger import logger
from helper.jwt import token_required
from core.redis_client import redis_client as r

@token_required
def onDisconnection(current_user):
    try:
        r.hset(f"user:{current_user.id}", 'connected', 'false')
        # self.nb_conn -= 1
        return {"status":"success"}, 200
    except RedisError as e:
        logger.critical("proxy onDisconnection error redis: " + str(e))
        return {"status":"error"}, 500
    except Exception as e:
        logger.critical("proxy onDisconnection args error: " + str(e))
        return {"status":"error"}, 500