import flask
from logger import logger
from schema.database import SessionLocal
from schema.models import User


def _apply_user_patch(user, payload):
    field_map = {
        "name": "name",
        "image": "image",
        "notifToken": "notif_token",
        "visible": "visible",
        "connected": "connected",
        "scale": "scale",
        "offsetX": "offset_x",
        "offsetY": "offset_y",
        "lng": "lng",
        "lat": "lat",
        "bot": "bot",
    }
    for api_field, model_field in field_map.items():
        if api_field in payload:
            setattr(user, model_field, payload[api_field])


def _serialize_user(user):
    return {
        "id": user.id,
        "name": user.name,
        "image": user.image,
        "notifToken": user.notif_token,
        "visible": user.visible,
        "connected": user.connected,
        "scale": user.scale,
        "offsetX": user.offset_x,
        "offsetY": user.offset_y,
        "lng": user.lng,
        "lat": user.lat,
        "bot": user.bot,
    }


def postGraphqlUser(payload):
    db = SessionLocal()
    try:
        user_id = payload.get("id")
        if not user_id:
            return {"data": {"updateUser": None}, "errors": ["Missing id"]}

        user = db.get(User, user_id)
        if user is None:
            user = User(id=user_id)
            db.add(user)

        _apply_user_patch(user, payload)
        db.commit()
        db.refresh(user)
        return {"data": {"updateUser": _serialize_user(user)}}
    except Exception as e:
        db.rollback()
        logger.critical("proxy postGraphqlUser error: " + str(e))
        return {"data": {"updateUser": None}, "errors": [str(e)]}
    finally:
        db.close()


def postGraphqlUserEntry():
    try:
        request = flask.request
        request_json = request.get_json() or {}
        return postGraphqlUser(request_json)
    except Exception as e:
        logger.critical("proxy postGraphqlUserEntry args error: " + str(e))
        return {"data": {"updateUser": None}, "errors": [str(e)]}

