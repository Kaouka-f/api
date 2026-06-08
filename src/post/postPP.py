import flask
from logger import logger
from redisIface import RedisIface
from utils import createFile


def postPP(id, pp):
    redis = RedisIface()
    try:
        # Check if id is valid
        id = redis.check_id(id)
        if id is None:
            del redis
            logger.critical("proxy postPP id error")
            return {}
        file_present = False
        ppname = ""
        if pp is not None:
            # TODO: need authentication
            ppname = createFile(pp, id)
            file_present = True
        if file_present:
            redis.redis_hset(id, 'img', ppname)
        del redis
        return ppname
    except Exception as e:
        logger.critical(
            "proxy Error while working postPP with Redis: " + str(e))
        return 'unset'


def postPPEntry():
    try:
        request = flask.request
        id = request.args.get('id')
        pp = None
        if 'file' in request.files:
            pp = request.files['file']
            print(request.files['file'])
        return postPP(id, pp)
    except Exception as e:
        logger.critical("proxy postPPEntry args error: " + str(e))
        return 'unset'
