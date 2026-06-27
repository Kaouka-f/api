from logger import logger
import flask
from flask import g
import utils

from sqlalchemy import select

from schema.models import User

def connect(email, password):
    db = g.db
    try:
        user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()

        if not user or user.password != password:
            return {"error": "Email ou mot de passe incorrect"}, 401
        # TODO: handle notif token
        # token = redis.redis_hget(id, 'notifToken')
        # utils.delete_fcm_instance(token)
        
        # TODO: JWT
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

        return {"connection":"sucess"}, 200
    except Exception as e:
        print(f"Error while working with MongoDB: {e}")

def connectEntry():
    try:
        request = flask.request
        request_json = request.get_json()
        email = request_json['email']
        password = request_json['password']
        print(f"Received email: {email}, password: {password}")
        if not email or not password:
            return {"presubscribe": True, "info": "missing_fields"}
        return connect(email, password)
    except Exception as e:
        logger.critical("proxy postConnect args error: " + str(e))
        return {}