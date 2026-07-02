import flask
from redis.exceptions import RedisError
from logger import logger
from redisIface import RedisIface
import datetime

from flask import g

from sqlalchemy import select

from schema.models import User


def onConnection(id):
    redis = RedisIface()
    db = g.db
    try:
        # Check if id is valid
        id = redis.check_id(id)
        if id == None:
            del redis
            logger.critical("proxy onConnection id error")
            return {}
        print(datetime.date.today())
        user = db.execute(select(User).where(User.id == id)).scalar_one_or_none()
        if user:
            user.last_conn = datetime.date.today()
            db.commit()
        else:
            logger.critical("proxy onConnection user not found")
            del redis
            return {}
        redis.redis_hset(f"user:{id}", 'connected', 'true')
        del redis
        return {}
    except RedisError as e:
        del redis
        logger.critical("proxy onConn error redis: " + str(e))
        return {}
    except Exception as e:
        del redis
        logger.critical("proxy onConn args error: " + str(e))
