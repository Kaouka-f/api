import redis
from redis.exceptions import RedisError
import os
from logger import logger


class RedisIface:
    def __init__(self):
        try:
            # unix socket
            # redis_socket_path = os.getenv("SOCKET_REDIS")
            # self.redis = redis.Redis(unix_socket_path=redis_socket_path)
            # tcp
            redis_host = "localhost"
            redis_port = 6379
            self.redis = redis.StrictRedis(
                host=redis_host, port=redis_port, decode_responses=True)
        except Exception as e:
            print("Redis connection error: " + str(e))
            exit(1)

    def __del__(self):
        self.redis.close()
        del self.redis

    def close(self):
        self.redis.close()
        del self.redis

    def redis_ttl(self):
        pass
        # return self.redis.ttl()

    def redis_expireat(self, key, expireSet):
        self.redis.expireat(key, expireSet)

    def redis_geoadd(self, long, lat, id):
        return self.redis.execute_command('GEOADD', 'locations', long, lat, id)

    def redis_georadius(self, long, lat, distance):
        return self.redis.execute_command('GEORADIUS', 'locations', long, lat, distance, 'm', 'WITHDIST')

    def redis_hset(self, key, field, value):
        keyEncoded = key
        fieldEncoded = field
        valueEncoded = value
        return self.redis.hset(keyEncoded, fieldEncoded, valueEncoded)

    def redis_hget(self, key, field):
        res = ""
        if self.redis.hexists(key, field):
            res = self.redis.hget(key, field)
        return res

    def redis_hgetall(self, key):
        try:
            keyEncoded = key
            res = self.redis.hgetall(keyEncoded)
            print(res)
            print(res.items())
            decoded_result = {}
            if res:
                decoded_result = {key: value for key, value in res.items()}
            return decoded_result
        except Exception as e:
            print(e)

    def redis_deleteall(self, key):
        keyEncoded = key
        return self.redis.delete(keyEncoded)

    def redis_delete(self, key, field):
        keyEncoded = key
        fieldEncoded = field
        return self.redis.hdel(keyEncoded, fieldEncoded)

    def redis_deletereq(self, id, reqId):
        idEncoded = (id)
        self.redis_delete(idEncoded, reqId)
        self.redis_delete(idEncoded, reqId+':expireSet')
        self.redis_delete(idEncoded, reqId+':reqTime')
        self.redis_delete(idEncoded, reqId+':file')
        # TODO: delete file using pub/sub mechanism

    def redis_postreq(self, id, reqId):
        # TODO: post req
        pass

    def redis_zrem(self, key, field):
        self.redis.zrem(key, field)

    def check_id(self, encodedId):
        return None
