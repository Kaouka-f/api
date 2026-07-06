import json
import flask
from logger import logger
from redisIface import RedisIface
from helper.jwt import token_required

@token_required
def getComments(id, lastReqId):
    # arg check
    size = 40960
    try:
        redis = RedisIface()
        if redis.redis.hexists(id, 'comments') == 0:
            del redis
            return {}
        comments_json_array = redis.redis_hget(id, 'comments')
        if comments_json_array == None or comments_json_array == '':
            del redis
            return {}
        comments = json.loads(comments_json_array)
        json_object = {}
        member_num = 0
        startIndex = 0
        if lastReqId and lastReqId != '':
            startIndex = comments.index(lastReqId)
        for commentID in comments[startIndex:]:
            comment = redis.redis_hgetall(commentID)
            if comment:
                personid = redis.redis_hget(comment['commentId'], 'id')
                infos = redis.redis_hgetall(personid)
                if infos:
                    comment['name'] = infos['name'] if 'name' in infos else "undefined"
                    comment['picture'] = infos['img'] if 'img' in infos else "https://elaborium.site/proxy/stream/default/profile.jpg"
                    comment['scale'] = infos['scale'] if 'scale' in infos else "1"
                    comment['offsetX'] = infos['offsetX'] if 'offsetX' in infos else "0"
                    comment['offsetY'] = infos['offsetY'] if 'offsetY' in infos else "0"
                    comment['connected'] = infos['connected'] if 'connected' in infos else "false"
                    if (len(str(json_object).encode('utf-8')) + len(str(comment).encode('utf-8'))) < size:
                        json_object[member_num] = comment
                        member_num+=1
                    else:
                        break
            else:
                comments_list = json.loads(comments_json_array)
                comments_list.remove(commentID)
                updated_json_array = json.dumps(comments_list)
                redis.redis_hset(id, "comments", updated_json_array)
                commentNb = redis.redis_hget(commentID, "commentNb")
                if commentNb != None and commentNb != "":
                    commentNb = int(commentNb)
                    commentNb -= 1
                    redis.redis_hset(commentID, "commentNb", str(commentNb))
        del redis
        return json_object
    except Exception as e:
            logger.critical("proxy getComments error: " + str(e))
            del redis
            return {}

def getCommentsEntry():
    try:
        request = flask.request
        id = request.args.get('id')
        lastReqId = request.args.get('lastReqId')
        return getComments(id, lastReqId)
    except Exception as e:
        logger.critical("proxy getCommentsEntry args error: " + str(e))
        return {}