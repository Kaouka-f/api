import base64
from datetime import datetime, timezone
import json
import os
import uuid
import flask
from redis.exceptions import RedisError
from logger import logger
from redisIface import RedisIface
from firebase_admin import credentials, messaging
import firebase_admin
from utils import createFile, sendNotif, mediaType


def sendMsg(targetPersonId, personId, message, file):
    redis = RedisIface()
    try:
        # Check if id is valid
        personId = redis.check_id(personId)
        if personId == None:
            del redis
            logger.critical("proxy sendMsg id error")
            return {'result': "false"}
        # TODO check isBlocked user
        req_result = redis.redis_hget(targetPersonId, 'blockedUser')
        if req_result != "":
            requests_list = json.loads(req_result)
            if personId in requests_list:
                return {'result': "blocked"}
        # create file
        media = ""
        if file:
            media = createFile(file, personId, "msgs/")
        # push msg in redis
        msgid = str(uuid.uuid4())
        current_time_utc = datetime.now(timezone.utc)
        timestamp = current_time_utc.timestamp()
        redis.redis_hset("msg:"+msgid, 'personId', personId)
        redis.redis_hset("msg:"+msgid, 'message', message)
        redis.redis_hset("msg:"+msgid, 'media', media)
        redis.redis_hset("msg:"+msgid, 'ts', timestamp)

        # push msg in user
        badge = 0
        msg_list_json = redis.redis_hget(targetPersonId, 'msgs')
        msg_list = []
        if msg_list_json != None and msg_list_json != "":
            msg_list = json.loads(msg_list_json)
            msg_list.append(msgid)
        else:
            msg_list = []
            msg_list.append(msgid)
        updated_json_array = json.dumps(msg_list)
        badge = len(msg_list)
        redis.redis_hset(targetPersonId, 'msgs', updated_json_array)
        # send notif
        pseudo = redis.redis_hget(personId, 'name')
        token = redis.redis_hget(targetPersonId, 'notifToken')
        msgRet = sendNotif(token, pseudo, message, badge)
        logger.error(msgRet)
        del redis
        return {'result': "true", 'media': media}
    except RedisError as e:
        del redis
        logger.critical("proxy sendMsg error redis: " + str(e))
        return {'result': "false"}
    except Exception as e:
        del redis
        logger.critical("proxy sendMsg args error: " + str(e))
        return {'result': "false"}


def sendMsgEntry():
    try:
        request = flask.request
        request_json = request.get_json()
        targetPersonId = request_json['targetPersonId']
        personId = request_json['personId']
        message = request_json['message']
        # filename = request_json['filename']
        # ext = request_json['ext']
        file = None
        if 'file' in request.files:
            file = request.files['file']
        return sendMsg(targetPersonId, personId, message, file)
    except Exception as e:
        logger.critical("proxy sendMsg args error: " + str(e))
        return {'result': 'false'}
