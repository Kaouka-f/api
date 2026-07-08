import flask
from redis.exceptions import RedisError
from logger import logger
from helper.jwt import token_required
from core.redis_client import redis_client as r

@token_required
def visibleEntry(current_user, value):
    try:
        request = flask.request
        request_json = request.get_json()
        value = request_json['value']
        if value == 'true':
            r.hset(f'user:{current_user.id}', 'visible', "1")
        elif value == 'false':
            r.hset(f'user:{current_user.id}', 'visible', "0")
        else:
            return {"status":"error"}, 400
        return {"status":"success"}, 200
    except RedisError as e:
        print(f"Error while working with Redis: {e}")
        return {"status":"error"}, 500
    except Exception as e:
        logger.critical("proxy get arrounds args error: " + str(e))
        return {"status":"error"}, 500