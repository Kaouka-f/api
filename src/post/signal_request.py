import json
import flask
from redis.exceptions import RedisError
from logger import logger
from redisIface import RedisIface

def signal(id, reqId):
    redis = RedisIface()
    try:
        # Check if id is valid
        id = redis.check_id(id)
        if id == None:
            del redis
            logger.critical("proxy signal id error")
            return {}
        if redis.redis.hexists(reqId, "signalNb") == 0:
            redis.redis_hset(reqId, "signalNb", "0")
        if redis.redis.hexists(reqId, "signals") == 0:
            redis.redis_hset(reqId, "signals", "[]")
        signalsJson = redis.redis_hget(reqId, "signals")
        signalsNb = redis.redis_hget(reqId, "signalNb")
        signals = json.loads(signalsJson)
        if id not in signals:
            signals.append(id)
            signalsNb = int(signalsNb) + 1
        else:
            signals.remove(id)
            signalsNb = int(signalsNb) - 1
        newsignals = json.dumps(signals)
        redis.redis_hset(reqId, "signalNb", str(signalsNb))
        redis.redis_hset(reqId, "signals", newsignals)
        # send to moderator
        logger.info("signal sent to moderator, reqId: " + reqId)
        del redis
        return "false"
    except RedisError as e:
        print(f"Error while working with Redis: {e}")
        return "true"
    except Exception as e:
        logger.critical("proxy signal args error: " + str(e))

def signalEntry():
    try:
        request = flask.request
        request_json = request.get_json()
        id = request_json['id']
        reqId = request_json['reqId']
        return signal(id, reqId)
    except Exception as e:
        logger.critical("proxy visibleEntry args error: " + str(e))
        return {}