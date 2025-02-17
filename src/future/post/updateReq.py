import flask
from redis.exceptions import RedisError
from logger import logger
from redisIface import RedisIface

def updateReq(id, reqId, newReq):
    redis = RedisIface()
    try:
        # Check if id is valid
        id = redis.check_id(request_json['id'])
        if id == None:
            del redis
            logger.critical("proxy updateReq id error")
            return {}
        reqId = request_json['reqId']
        newReq = request_json['newReq']
    except Exception as e:
        logger.critical("proxy get arrounds args error: " + str(e))
    # TODO: need authentication
    try:
        if redis.redis_hget('req_'+id, reqId) != newReq:
            res = redis.redis_hset('req_'+id, reqId, newReq)
            # send to analyzer
            # try:
            #     analyzer_data = json.dumps({'req': 'request', 'request':newReq, 'reqId':reqId, 'personId':id}).encode('utf-8')
            #     self.socket_analyzer.send(analyzer_data)
            # except Exception as err:
            #     self.logger.info("get arrounds failed to send to analyzer: %s", err)
            #     self.log.log_crash("proxy get arrounds failed to send to analyzer: " + str(err))
            return {'reqChanged': res}
        return {'reqChanged': 'true'}
    except RedisError as e:
        print(f"Error while working with Redis: {e}")
        return {}