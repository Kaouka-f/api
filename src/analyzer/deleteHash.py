import flask
from redis.exceptions import RedisError
from logger import logger
from redisIface import RedisIface
from post.deleteReq import deleteReqStatic
from post.deleteAccount import deleteAccountStatic

def deleteHash(password, hash):
    try:
        print(password)
        print(hash)
        redis = RedisIface()
        response = {}
        # TODO: create JWT for bot creation
        if password == 'zigzag':
            hashSet = redis.redis_hgetall(hash)
            if "privateId" in hashSet or "bot" in hashSet or "lastConn" in hashSet:
                print('account')
                print(deleteAccountStatic(redis, hash))
            elif "reqId" in hashSet or "reqTime" in hashSet or "likes" in hashSet:
                print('req')
                print(deleteReqStatic(redis, hash))
            else:
                print('else')
                print(redis.redis_deleteall(hash))
        del redis
        return response
    except RedisError as e:
        logger.critical("proxy deleteHash error redis: " + str(e))
        del redis
        return {}

def deleteHashEntry():
    try:
        request = flask.request
        request_json = request.get_json()
        password = request_json['password']
        hash = request_json['hash']
        return deleteHash(password, hash)
    except Exception as e:
        logger.critical("proxy deleteHashEntry args error: " + str(e))
        return {}