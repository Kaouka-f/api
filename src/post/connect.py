from redisIface import RedisIface
from logger import logger
import flask
import utils

def connect(id):
    redis = RedisIface()
    try:
        id = redis.check_id(id)
        if id == None:
            del redis
            logger.warning("connection failed")
            return {"connection":"failed"}
        token = redis.redis_hget(id, 'notifToken')
        utils.delete_fcm_instance(token)
        return {"connection":"sucess"}
        # JWT
        # JWT creation
        # payload = {
        #     "user_id": 123,
        #     "username": "john_doe",
        #     "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Expiry time
        # }
        # secret_key = "your-secret-key"
        # token = jwt.encode(payload, secret_key, algorithm="HS256")
        # JWT use
        # TODO: get secret key in database, make token in arg
        # token = ""
        # secret_key = ""
        # decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
        # print(decoded_token)
        # return {'connected': False, 'key': token}
    except Exception as e:
        print(f"Error while working with MongoDB: {e}")

def connectEntry():
    try:
        request = flask.request
        request_json = request.get_json()
        id = request_json['id']
        return connect(id)
    except Exception as e:
        logger.critical("proxy postNameEntry args error: " + str(e))
        return {}