import flask
from logger import logger
from redisIface import RedisIface
from helper.file import createFile
from helper.jwt import token_required
from core.redis_client import redis_client as r

@token_required
def postPPEntry(current_user):
    try:
        request = flask.request
        pp = None
        if 'file' in request.files:
            pp = request.files['file']
            print(request.files['file'])
        file_present = False
        ppname = ""
        if pp is not None:
            ppname = createFile(pp, current_user.id)
            file_present = True
        if file_present:
            r.hset(f"user:{current_user.id}", 'img', ppname)
        return {"status": "success", "data": {"ppname": ppname}}, 200
    except Exception as e:
        logger.critical(
            "proxy Error while working postPP with Redis: " + str(e))
        return {"status": "error", "message": "Internal server error"}, 500