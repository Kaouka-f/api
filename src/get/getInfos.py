import flask
from logger import logger
from redisIface import RedisIface
from helper.jwt import token_required

@token_required
def getInfos(personid):
    try:
        if personid:
            redis = RedisIface()
            json_object = {}
            infos = redis.redis_hgetall(f"user:{personid}")
            json_object['name'] = infos['name'] if 'name' in infos else "undefined"
            json_object['img'] = infos['img'] if 'img' in infos else "https://elaborium.site/proxy/stream/default/profile.jpg"
            json_object['scale'] = infos['scale'] if 'scale' in infos else "1"
            json_object['offsetX'] = infos['offsetX'] if 'offsetX' in infos else "0"
            json_object['offsetY'] = infos['offsetY'] if 'offsetY' in infos else "0"
            json_object['connected'] = infos['connected'] if 'connected' in infos else "false"
            if infos['bot'] == 'true':
                json_object['lng'] = infos['lng']
                json_object['lat'] = infos['lat']
            del redis
            return json_object
        else:
            del redis
            return {}

    except Exception as e:
            del redis
            logger.critical("proxy get infos error: " + str(e))
            return {}

def getInfosEntry():
    try:
        request = flask.request
        personid = request.args.get('personid')
        return getInfos(personid)
    except Exception as e:
        logger.critical("proxy getInfosEntry args error: " + str(e))
        return {}