from logger import logger
from flask import g
from helper.jwt import revoke_persistent_token
from helper.jwt import token_required

@token_required
def disconnect(current_user):
    try:
        # TODO: delete the persistent token from the database or Redis
        revoke_persistent_token(current_user.id)
        return {"status":"success"}, 200
    except Exception as e:
        print(f"kaouka internal error: : {e}")
        return {"status":"error"}, 500

def disconnectEntry():
    try:
        return disconnect()
    except Exception as e:
        logger.critical("proxy postConnect args error: " + str(e))
        return {"status":"error"}, 500