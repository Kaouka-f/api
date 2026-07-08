import datetime
import os
from logger import logger
import flask
from flask import g
from helper.jwt import create_persistent_token, create_session_token
from sqlalchemy import select
from schema.models import User

def connect(email, password, notif_token=None):
    db = g.db
    try:
        user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()

        if not user or user.password != password:
            return {"status": "error", "message": "Email ou mot de passe incorrect"}, 401
        
        
        # connexion infos
        user.last_conn = datetime.date.today()
        db.commit()

        # notif token
        if user.notif_token and user.notif_token != notif_token:
            # token = redis.redis_hget(id, 'notifToken')
            # utils.delete_fcm_instance(notif_token)
            print(f"notif token changed for user {user.id}: {user.notif_token} -> {notif_token}")
            user.notif_token = notif_token
            db.commit()
        
        # JWT persistent token creation
        persistent_token = create_persistent_token(user.id, email)

        # JWT access token creation
        session_token = create_session_token(user.id)

        return {"status": "success", "data": {"session_token": session_token, "persistent_token": persistent_token}}, 200
    except Exception as e:
        print(f"kaouka internal error: : {e}")
        return {"status": "error", "message": "Internal server error"}, 500

def connectEntry():
    try:
        request = flask.request
        request_json = request.get_json()
        email = request_json['email']
        password = request_json['password']
        notif_token = request_json.get('notifToken', None)
        print(f"Received email: {email}, password: {password}, notifToken: {notif_token}")
        if not email or not password:
            return {"status": "error", "message": "missing_fields"}
        return connect(email, password, notif_token)
    except Exception as e:
        logger.critical("proxy postConnect args error: " + str(e))
        return {"status": "error", "message": "Internal server error"}, 500