import json
import flask
from logger import logger
from redisIface import RedisIface

def getMsgs(id, thold):
    size = 40960
    try:
        redis = RedisIface()
        # Check if id is valid
        id = redis.check_id(id)
        if id == None:
            del redis
            logger.critical("proxy getMsg id error")
            return {}
        req_result = {}
        member_num = 0
        msgListLen = 0
        if redis.redis.hexists(id, 'msgs'):
            msg_list_json = redis.redis_hget(id, 'msgs')
            if msg_list_json:
                msg_list = json.loads(msg_list_json)
                msgListLen = len(msg_list)
                for msg in msg_list[thold:]:
                    message = {}
                    msg_json = redis.redis_hgetall("msg:"+msg)
                    if msg_json:
                        print(msg_json)
                        message['personId'] = msg_json["personId"]
                        message['message'] = msg_json["message"]
                        message['media'] = msg_json["media"]
                        message['ts'] = msg_json["ts"]
                    if (len(str(req_result).encode('utf-8')) + len(str(message).encode('utf-8'))) < size:
                        req_result[member_num] = message
                        member_num+=1
                    else:
                        break
        del redis
        return {'msgs':req_result, 'rest':msgListLen - member_num, 'thold':thold+member_num}
    except Exception as e:
        # del redis
        logger.critical("proxy getMsg args error: " + str(e))

def getMsgsEntry():
    try:
        request = flask.request
        id = request.args.get('id')
        thold = int(request.args.get('thold'))
        return getMsgs(id, thold)
    except Exception as e:
        logger.critical("proxy getMsgEntry args error: " + str(e))
        return {}