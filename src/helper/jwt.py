from datetime import datetime, timedelta, timezone

import jwt
import os
from flask import jsonify
import flask
from functools import wraps
from flask import g
from core.redis_client import redis_client as r

from schema.models import User

SECRET_KEY = os.environ.get("SECRET_KEY")
EXPIRED_DELAY = 30 * 24 * 3600



def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        db = g.db
        token = None

        # Extract token from the Authorization header
        if 'Authorization' in flask.request.headers:
            token = flask.request.headers['Authorization'].split(" ")[1]  # "Bearer <token>"

        if not token:
            return jsonify({"error": "Token manquant"}), 401

        try:
            # decode token
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = db.session.query(User).get(payload['user_id'])

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expiré"}), 401
        except jwt.InvalidTokenError:
            # TODO: disconnect user by removing the persistent token from the database
            return jsonify({"error": "Token invalide"}), 401

        return f(current_user, *args, **kwargs)

    return decorated

# USE: @token_required in fuctions that require authentication. The current_user will be passed as the first argument to the function.

def create_session_token(user_id):
    payload = {
        "user_id": str(user_id),
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15)  # ← session
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def create_persistent_token(user_id, email):
    payload = {
        "user_id": str(user_id),
        "email": email,
        "type": "persistent",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=EXPIRED_DELAY) 
    }
    persistent_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")    
    r.setex(
        f"{user_id}:persistent_token",
        EXPIRED_DELAY,
        persistent_token
    )
    return persistent_token

# Au persistent → vérifier qu'il est valide
def verify_persistent_token(user_id, persistent_token):
    stored = r.get(f"{user_id}:persistent_token")
    if stored.decode() != persistent_token:
        revoke_persistent_token(user_id)
        return "invalid"
    elif stored is None:
        return "expired"
    elif stored.decode() == persistent_token:
        return "valid"
    return "invalid"
    

# Au logout → supprimer
def revoke_persistent_token(user_id):
    r.delete(f"{user_id}:persistent_token")