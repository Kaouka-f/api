from logger import logger
from helper.jwt import token_required
from core.redis_client import redis_client as redis

@token_required
def getInfosEntry(current_user):
    try:
        json_object = {}
        infos = redis.hgetall(f"user:{current_user['user_id']}")
        json_object['name'] = infos['name'] if 'name' in infos else "undefined"
        json_object['img'] = infos['img'] if 'img' in infos else "https://elaborium.site/proxy/stream/default/profile.jpg"
        json_object['scale'] = infos['scale'] if 'scale' in infos else "1"
        json_object['offsetX'] = infos['offsetX'] if 'offsetX' in infos else "0"
        json_object['offsetY'] = infos['offsetY'] if 'offsetY' in infos else "0"
        json_object['connected'] = infos['connected'] if 'connected' in infos else "false"
        if infos['bot'] == 'true':
            json_object['lng'] = infos['lng']
            json_object['lat'] = infos['lat']
        return {"status": "success", "data": json_object}, 200
    
    except Exception as e:
            logger.critical("proxy get infos error: " + str(e))
            return {"status": "error", "message": "Internal server error"}, 500