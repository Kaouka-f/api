import flask
from logger import logger
from helper.jwt import token_required
from core.redis_client import redis_client as r

@token_required
def postPPSettingEntry(current_user, scale, offsetX, offsetY):
    try:
        request = flask.request
        request_json = request.get_json()
        scale = request_json['scale']
        offsetX = request_json['offsetX']
        offsetY = request_json['offsetY']
        r.hset(f"user:{current_user.id}", 'scale', scale)
        r.hset(f"user:{current_user.id}", 'offsetX', offsetX)
        r.hset(f"user:{current_user.id}", 'offsetY', offsetY)
        return {"status": "success"}, 200
    except Exception as e:
        logger.critical("proxy Error while working postPPSetting with Redis: " + str(e))
        return {"status": "error"}, 500