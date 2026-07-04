import datetime

import jwt
import os

from logger import logger
import flask
from flask import g
from api.src.token import create_persistent_token, create_session_token

from sqlalchemy import select

from schema.models import User

SECRET_KEY = os.environ.get("SECRET_KEY")
EXPIRED_DELAY = 30 * 24 * 3600

def connect(email, password, notif_token):
    db = g.db
    try:
        user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()

        if not user or user.password != password:
            return {"error": "Email ou mot de passe incorrect"}, 401
        
        # notif token
        user = db.execute(select(User).where(User.id == id)).scalar_one_or_none()
        if user:
            # token = redis.redis_hget(id, 'notifToken')
            # utils.delete_fcm_instance(notif_token)
            user.notif_token = notif_token
            db.commit()
        
        # JWT persistent token creation
        persistent_token = create_persistent_token(user.id)

        # JWT access token creation
        session_token = create_session_token(user.id)

        return {"connection":"sucess", "session_token": session_token, "persistent_token": persistent_token}, 200
    except Exception as e:
        print(f"Error while working with MongoDB: {e}")

def connectEntry():
    try:
        request = flask.request
        request_json = request.get_json()
        email = request_json['email']
        password = request_json['password']
        notif_token = request_json.get('notifToken', None)
        print(f"Received email: {email}, password: {password}")
        if not email or not password:
            return {"presubscribe": True, "info": "missing_fields"}
        return connect(email, password, notif_token)
    except Exception as e:
        logger.critical("proxy postConnect args error: " + str(e))
        return {}