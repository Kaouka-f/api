import uuid
import flask
from flask import g
from logger import logger

from sqlalchemy import select

from schema.models import User


def signUp(password, email):
    db = g.db
    try:
        exist = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if exist:
            return {"presubscribe": True, "info": "user_exists"}

        # PROPER WAY TO GENERATE ID

        # TODO: check password strength, email format, etc. (validation côté client aussi)
        
        # TODO: Send id to confirmation
        # data = {'req_type': 'confirmation' ,'id': id}
        # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #     s.connect(("confirmation-service", 6000))
        #     s.sendall(data.encode())
        
        # TODO: Generate and send mail
        # link = create_confirmation_link(id)
        # send_confirmation_email(email, link)
        
        # TODO: encrypt password before storing it in the database (e.g., using bcrypt)

        user = User(
            id=str(uuid.uuid4()),
            email=email,
            password=password,
        )
        db.add(user)
        db.flush()  # envoie l'INSERT sans commit (le teardown_request committe)

        return {"presubscribe": False, "info": user.id}

    except Exception as e:
        logger.error("signUp error: " + str(e))
        return {"presubscribe": True}


def signUpEntry():
    try:
        request = flask.request
        request_json = request.get_json()
        email = request_json['email']
        password = request_json['password']
        if not email or not password:
            return {"presubscribe": True, "info": "missing_fields"}
        return signUp(password=password, email=email)
    except Exception as e:
        logger.critical("signUpEntry args error: " + str(e))
        return {'res': "true"}
