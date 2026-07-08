import flask
from logger import logger
from helper.jwt import token_required
from core.redis_client import redis_client as r

@token_required
def postNameEntry(current_user, name):
    try:
        request = flask.request
        request_json = request.get_json()
        id = request_json['id']
        name = request_json['name']
        r.hset(f"user:{current_user.id}", 'name', name)
        return {"status": "success"}, 200
    except Exception as e:
        logger.critical("proxy Error while working postName with Redis: " + str(e))
        return {"status": "error", "message": "Internal server error"}, 500