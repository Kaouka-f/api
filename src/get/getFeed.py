import flask
from redis.exceptions import RedisError
from logger import logger
from helper.media import get_random_file_in_folder
from redisIface import RedisIface

FILE_PATH = '/opt/files/videos'
PREFIX_URL = "http://192.168.1.22:8001/videos/"

def getFeed(id):
    try:
        redis = RedisIface()
        # Check if id is valid
        id = redis.check_id(id)
        if id == None:
            del redis
            logger.critical("proxy getFeed id error")
            return {}
        # Get feed
        response_data = []
        for _ in range(10):
            response_data.append(PREFIX_URL+get_random_file_in_folder(FILE_PATH))
        del redis
        return {'feed': response_data}
    except RedisError as e:
        logger.critical("proxy getFeed error redis: " + str(e))
        del redis
        return {}

def getFeedEntry():
    try:
        request = flask.request
        id = request.args.get('id')
        return getFeed(id)
    except Exception as e:
        logger.critical("proxy getFeedEntry args error: " + str(e))
        return {}