import json
import time
import uuid
import flask
from logger import logger
from redisIface import RedisIface
from redis.exceptions import RedisError
import os
from utils import createFile

from schema.database import SessionLocal
from schema.models import Request, User

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'mkv', 'webm'}
FILE_PATH = '/opt/files/'
def allowed_file(filename):
    return '.' in filename and \
       filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def postReq(id, req, file):
    redis = RedisIface()
    session = SessionLocal()
    file_present = False
    # save file if present
    try:
        # Check if id is valid
        id = redis.check_id(id)
        if id == None:
            del redis
            logger.critical('proxy postReq id error')
            return {'res':"false"}
        file_present = False
        media = ''
        if file != None:
            media = createFile(file, id)
            if(media == None):
                del redis
                return {'res':"true"}
            file_present = True
        if req or file_present:
            reqId = str(uuid.uuid4())
            # TODO: use audio, video, image, text, etc. instead of file
            if file_present:
                redis.redis_hset(reqId, "media", media)
            redis.redis_hset(reqId, "id", id)
            redis.redis_hset(reqId, "reqId", reqId)
            redis.redis_hset(reqId, "text", req)
            redis.redis_hset(reqId, "reqTime", str(time.time()))
            redis.redis_hset(reqId, "commentNb", "0")
            redis.redis_hset(reqId, "likeNb", "0")
            redis.redis_hset(reqId, "likes", json.dumps([]))
            requests_json_array = redis.redis_hget(id, 'requests')
            requests_list = []
            if requests_json_array != None and requests_json_array != "":
                requests_list = json.loads(requests_json_array)
                requests_list.append(reqId)
            else:
                requests_list.append(reqId)
            updated_json_array = json.dumps(requests_list)
            redis.redis_hset(id, "requests", updated_json_array)
            del redis
            return {'res':"false"}
        else:
            del redis
            return {'res':"true"}
    except RedisError as e:
        del redis
        print(f"Error while working with Redis: {e}")
        return {'res':"true"}
    except Exception as e:
        del redis
        logger.critical("post req error: " + str(e))
        return {'res':"true"}

def postReqEntry():
    try:
        request = flask.request
        id = request.args.get('id')
        req = request.args.get('request')
        file = None
        if 'file' in request.files:
            file = request.files['file']
        return postReq(id, req, file)
    except Exception as e:
        logger.critical("proxy postReqEntry args error: " + str(e))
        return {'res':"true"}