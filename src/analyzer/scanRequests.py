import flask
from redis.exceptions import RedisError
from logger import logger
from redisIface import RedisIface

def scanRequests(password, cursor, match_pattern=None, field_to_match=None):
    try:
        redis = RedisIface()  # Assuming RedisIface is your interface class
        response = {}
        if password == 'zigzag':
            cursor, keys = redis.redis.scan(cursor=int(cursor), match=match_pattern)
            i = 0
            for key in keys:
                # Check if the key is a hash and contains the specified field
                if field_to_match:
                    if redis.redis.hexists(key, field_to_match):
                        response[i] = key
                        i += 1
                elif not field_to_match:
                    # If no field_to_match is specified, add all matching keys
                    response[i] = key
                    i += 1
        del redis
        return response
    except RedisError as e:
        logger.critical("proxy scanRequests error redis: " + str(e))
        return {}

def scanRequestsEntry():
    try:
        request = flask.request
        password = request.args.get('password')
        cursor = request.args.get('cursor')
        if request.args.get('match_pattern'): match_pattern = request.args.get('match_pattern') 
        else: match_pattern = None 
        if request.args.get('field_to_match'): field_to_match = request.args.get('field_to_match')
        else: field_to_match = None
        return scanRequests(password, cursor, match_pattern, field_to_match)
    except Exception as e:
        logger.critical("proxy scanRequestsEntry args error: " + str(e))
        return {}