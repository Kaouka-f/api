import jwt
from helper.jwt import create_session_token, verify_persistent_token
import flask
import os

SECRET_KEY = os.environ.get("SECRET_KEY", "default_secret_key")  # Use a default value for testing

def refresh():
    data = flask.request.get_json()
    persistent_token = str(data['persistent_token'])

    payload = jwt.decode(persistent_token, SECRET_KEY, algorithms=["HS256"])
    user_id = payload['user_id']

    status = verify_persistent_token(user_id, persistent_token)
    if status == "invalid":
        return {"status": "error"}, 401
    elif status == "expired":
        return {"status": "error"}, 401

    # Générer un nouveau session token
    new_session_token = create_session_token(user_id)

    return {"status": "success", "data": {"session_token": new_session_token}}, 200