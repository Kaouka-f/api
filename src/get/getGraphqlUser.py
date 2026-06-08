import flask
from logger import logger
from schema.database import SessionLocal
from schema.models import Request, User


def _serialize_user(user, requests):
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
        "requests": [
            {
                "id": req.id,
                "text": req.text,
                "media": req.media,
                "reqTime": req.req_time.isoformat() if req.req_time else None,
                "commentNb": req.comment_nb,
                "likeNb": req.like_nb,
                "signalNb": req.signal_nb,
            }
            for req in requests
        ],
    }


def getGraphqlUser(user_id, include_requests=True, limit=20):
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if user is None:
            return {"data": {"user": None}, "errors": ["User not found"]}

        req_query = db.query(Request).filter(Request.user_id == user_id).order_by(Request.req_time.desc())
        if include_requests:
            reqs = req_query.limit(limit).all()
        else:
            reqs = []

        return {"data": {"user": _serialize_user(user, reqs)}}
    except Exception as e:
        logger.critical("proxy getGraphqlUser error: " + str(e))
        return {"data": {"user": None}, "errors": [str(e)]}
    finally:
        db.close()


def getGraphqlUserEntry():
    try:
        request = flask.request
        user_id = request.args.get("id")
        include_requests = request.args.get("includeRequests", "true").lower() != "false"
        limit_raw = request.args.get("limit", "20")
        limit = int(limit_raw) if limit_raw and str(limit_raw).isdigit() else 20
        return getGraphqlUser(user_id, include_requests, limit)
    except Exception as e:
        logger.critical("proxy getGraphqlUserEntry args error: " + str(e))
        return {"data": {"user": None}, "errors": [str(e)]}

