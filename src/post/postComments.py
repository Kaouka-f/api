import json
import time
import uuid
import flask
from logger import logger
from redisIface import RedisIface
from redis.exceptions import RedisError
import os
from firebase_admin import messaging
from helper.file import createFile
from helper.firebase import sendNotif

def postComments(id, postId, comment, file):
    redis = RedisIface()
    # Check if id is valid
    id = redis.check_id(id)
    if id == None:
        del redis
        logger.critical("proxy postComments id error")
        return {}
    file_present = False
    filenames = []
    try:
        # save file if present
        if file != None:
            media = createFile(file, id)
            file_present = True
        commentId = str(uuid.uuid4())
        # TODO: use hmset instead
        if file_present:
            redis.redis_hset(commentId, "media", media)
        redis.redis_hset(commentId, "attachReqId", postId)
        redis.redis_hset(commentId, "commentId", commentId)
        redis.redis_hset(commentId, "id", id)
        redis.redis_hset(commentId, "text", comment)
        redis.redis_hset(commentId, "reqTime", str(time.time()))
        redis.redis_hset(commentId, "commentNb", "0")
        redis.redis_hset(commentId, "likeNb", "0")
        redis.redis_hset(commentId, "likes", json.dumps([]))
        # send notif to user
        personId = redis.redis_hget(postId, "id")
        token = redis.redis_hget(personId, "notifToken")
        pseudo = redis.redis_hget(id, "name")
        sendNotif(token, pseudo, "à commenté votre post")
        # add commentNb
        commentNb = redis.redis_hget(postId, "commentNb")
        if commentNb != None and commentNb != "":
            commentNb = int(commentNb)
        else:
            commentNb = 0
        commentNb += 1
        redis.redis_hset(postId, "commentNb", str(commentNb))
        # add comment in request key
        comments_json_array = redis.redis_hget(postId, 'comments')
        comments_list = []
        if comments_json_array != None and comments_json_array != "":
            comments_list = json.loads(comments_json_array)
            comments_list.append(commentId)
        else:
            comments_list = []
            comments_list.append(commentId)
        updated_json_array = json.dumps(comments_list)
        redis.redis_hset(postId, "comments", updated_json_array)
        # add in req of interressed
        reqOI_json_array = redis.redis_hget(id, 'requestsOfInterressed')
        reqOI_list = []
        if reqOI_json_array != None and reqOI_json_array != "":
            reqOI_list = json.loads(reqOI_json_array)
            reqOI_list.append(postId)
        else:
            reqOI_list = []
            reqOI_list.append(postId)
        updated_reqOI_json_array = json.dumps(reqOI_list)
        redis.redis_hset(id, "requestsOfInterressed", updated_reqOI_json_array)
        # send notif to reqId
        targetid = redis.redis_hget(postId, "id")
        notifToken = redis.redis_hget(targetid, "notifToken")
        pseudo = redis.redis_hget(targetid, "name")
        sendNotif(notifToken, pseudo, "à commenté ton post")
        del redis
        return {'res':'true'}
    except RedisError as e:
        del redis
        print(f"Error while working with Redis: {e}")
        return {}
    except Exception as e:
        del redis
        print(f"Error in postComments : {e}")
        return {}

def postCommentsEntry():
    try:
        request = flask.request
        id = request.args.get('id')
        postId = request.args.get('postId')
        comment = request.args.get('comment')
        file = None
        if 'file' in request.files and request.files.get('file').filename:
            file = request.args.get('file')
        return postComments(id, postId, comment, file)
    except Exception as e:
        logger.critical("proxy postCommentsEntry args error: " + str(e))
        return {}