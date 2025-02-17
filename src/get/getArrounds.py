import json
import flask
from redis.exceptions import RedisError
from logger import logger
from redisIface import RedisIface

def arrounds(id, long, lat):
    # init
    redis = RedisIface()
    result = {}
    member_num = 0
    size = 40960
    distance = 1000
    try:
        # Check if id is valid
        id = redis.check_id(id)
        if id == None:
            del redis
            logger.critical("proxy get arrounds id error")
            return {}
    except Exception as e:
        logger.critical("proxy get arrounds args error: " + str(e))
        print("proxy get arrounds args error: " + str(e))
    # process
    try:
        redis.redis_geoadd(long, lat, id)
        locations = ""
        while distance < 50000 and result == {}:
            locations = redis.redis_georadius(long, lat, distance)
            distance += 10000
            if not locations:
                return {}
            for location in locations:
                try:
                    member = location[0]
                    if member != id and member != "":
                        json_object = {}
                        # if redis.redis.sismember(member, 'visible'):
                        #     break
                        visible = redis.redis_hget(member, 'visible')
                        if visible != '1' and visible != '0': visible = '1'
                        if visible == '1':
                            req_result = redis.redis_hget(member, 'requests')
                            requests_list = []
                            if req_result:
                                requests_list = json.loads(req_result)
                            if requests_list:
                                try:
                                    req = requests_list[-1]
                                    request = redis.redis_hgetall(req)
                                    if request and member:
                                        personInfo = redis.redis_hgetall(member)
                                        json_object['distance'] = location[1]
                                        json_object['requests'] = request
                                        json_object['id'] = member
                                        json_object['name'] = personInfo['name'] if 'name' in personInfo else "undefined"
                                        json_object['picture'] = personInfo['img'] if 'img' in personInfo else  "https://elaborium.site/proxy/stream/default/profile.jpg"
                                        json_object['scale'] = personInfo['scale'] if 'scale' in personInfo else "1"
                                        json_object['offsetX'] = personInfo['offsetX'] if 'offsetX' in personInfo else "0"
                                        json_object['offsetY'] = personInfo['offsetY'] if 'offsetY' in personInfo else "0"
                                        json_object['connected'] = personInfo['connected'] if 'connected' in personInfo else "false"
                                        if (len(str(result).encode('utf-8')) + len(str(json_object).encode('utf-8'))) < size:
                                            result[member_num] = json_object
                                        else:
                                            break
                                        member_num+=1
                                except Exception as e:
                                    logger.critical("proxy get arrounds get request : " + 'member: '+str(member) + "error: " + str(e))
                                    print("proxy get arrounds get request : " + 'req_'+str(member) + "error: " + str(e))
                                    redis.redis_deleteall('req_'+str(member))
                except Exception as e:
                    logger.critical("proxy get arrounds get peoples arround member : " + str(member) + "error: " + str(e))
                    print("proxy get arrounds get peoples arround member : " + str(member) + "error: " + str(e))
                    redis.redis_zrem('locations', member)
    except RedisError as e:
        logger.critical("proxy get arrounds Error while working with Redis: " + str(e))
        print("proxy get arrounds Error while working with Redis: " + str(e))
        redis.redis_zrem('locations', id)
    except Exception as err:
        logger.critical("proxy get arrounds error while set locatiion: " + str(err))
        print("proxy get arrounds error while set locatiion: " + str(err))
    # send to analyzer
    # try:
    #     analyzer_data = json.dumps({'req': 'arrounds', 'id':id, 'long':long, 'lat':lat}).encode('utf-8')
    #     socket_analyzer.send(analyzer_data)
    # except Exception as err:
    #     logger.info("get arrounds failed to send to analyzer: %s", err)
    #     logger.critical("proxy get arrounds failed to send to analyzer: " + str(err))
    del redis
    return result

def arroundsEntry():
    try:
        request = flask.request
        id = request.args.get('id')
        long = request.args.get('long')
        lat = request.args.get('lat')
        return arrounds(id, long, lat)
    except Exception as e:
        logger.critical("proxy get arroundsEntry args error: " + str(e))
        return {}