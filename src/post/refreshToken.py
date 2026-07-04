import jwt
from api.src.token import create_session_token, verify_persistent_token
import flask
import os

SECRET_KEY = os.environ.get("SECRET_KEY")

def refresh():
    data = flask.request.get_json()
    persistent_token = data['persistent_token']

    payload = jwt.decode(persistent_token, SECRET_KEY, algorithms=["HS256"])
    user_id = payload['user_id']

    status = verify_persistent_token(user_id, persistent_token)
    if status == "invalid":
        return {"error": "Token invalide"}, 401
    elif status == "expired":
        return {"error": "Token expiré"}, 401

    # Générer un nouveau session token
    new_session_token = create_session_token(user_id)

    return {"session_token": new_session_token}, 200