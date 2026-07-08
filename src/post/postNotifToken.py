import flask
from flask import g
from logger import logger
from helper.jwt import token_required

@token_required
def postNotifTokenEntry(current_user, notifToken):
    db = g.db
    try:
        request = flask.request
        request_json = request.get_json()
        notifToken = request_json['notifToken']
        db.execute("UPDATE users SET notif_token = :notifToken WHERE id = :id", {"notifToken": notifToken, "id": current_user.id})
        return {"status": "success"}, 200
    except Exception as e:
        logger.critical("proxy Error while working postNotifToken with Redis: " + str(e))
        return {"status": "error", "message": "Internal server error"}, 500