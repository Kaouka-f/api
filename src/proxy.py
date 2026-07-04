import os
from flask import Flask, g
from flask_cors import CORS
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address

import flask
from logger import logger
from firebase_admin import credentials
import firebase_admin

from schema.database import SessionLocal, engine, Base

###########
# METHODS #
###########
# GET
from get.getArrounds import arroundsEntry
from get.getInfos import getInfosEntry
from get.getId import getId
from get.getComments import getCommentsEntry
from get.getOwnReqs import getOwnReqsEntry
from get.getLikes import getLikesEntry
from get.getAllReqs import getAllReqsEntry
from get.getRequest import getRequestEntry
from get.getFeed import getFeedEntry
from get.streamer import stream_file
from get.getMsgs import getMsgsEntry
from get.getInterressed import getInterressedEntry
from get.getGraphqlUser import getGraphqlUserEntry
from get.preview import previewEntry
from get.isBlocked import isBlockedEntry
# POST
from post.postReq import postReqEntry
from post.visible import visibleEntry
from post.postNotifToken import postNotifTokenEntry
from post.postName import postNameEntry
from post.postGraphqlUser import postGraphqlUserEntry
from post.postPP import postPPEntry
from post.postPPSetting import postPPSettingEntry
from post.onConnection import onConnection
from post.onDisconnection import onDisconnection
from post.deleteReq import deleteReqEntry
from post.postComments import postCommentsEntry
from post.likeReq import likeReqEntry
from post.deleteAccount import deleteAccountEntry
from post.signal_request import signalEntry
from post.sendMsg import sendMsgEntry
from post.connect import connectEntry
from post.deleteMsgs import deleteMsgsEntry
from post.deleteMsg import deleteMsgEntry
from post.deleteInterressed import deleteInterressedEntry
from post.blockUser import blockUserEntry
from post.postLocation import postLocationEntry
from post.signUp import signUpEntry
from post.refreshToken import refresh

# ANALYZER
from analyzer.getBots import getBotsEntry
from analyzer.createBot import createBotEntry
from analyzer.hashGetAll import hashGetAllEntry
from analyzer.postBotInfos import postBotInfosEntry
from analyzer.scanRequests import scanRequestsEntry
from analyzer.deleteHash import deleteHashEntry

# limiter = Limiter(
#     get_remote_address,
#     app=app,
#     default_limits=["200 per minute"],
#     storage_uri="memory://",
# )

mode = os.environ.get('MODE')


class Proxy:
    user_connected = 0

    def __init__(self):
        self.app = Flask(__name__)
        # server init
        CORS(self.app)
        @self.app.before_request
        def before_request():
            g.db = SessionLocal()

        @self.app.teardown_request
        def teardown_request(exception=None):
            db = getattr(g, "db", None)
            
            if db:
                try:
                    if exception:
                        db.rollback()
                    else:
                        db.commit()
                finally:
                    db.close()

        # firebase init
        try:
            if mode == 'test':
                cred = credentials.Certificate(
                    "./key/kaouka-460308906bec.json")
            else:
                cred = credentials.Certificate("/key/kaouka-460308906bec.json")
            app_name = f"firebase_app_{os.getpid()}"
            firebase_admin.initialize_app(cred, name=app_name)
        except Exception as e:
            logger.critical("init firebase error: " + str(e))

        self.app.route('/proxy/getArrounds', methods=['GET'])(arroundsEntry)
        self.app.route('/proxy/getInfos', methods=['GET'])(getInfosEntry)
        self.app.route('/proxy/getId', methods=['GET'])(getId)
        self.app.route('/proxy/getComments', methods=['GET'])(getCommentsEntry)
        self.app.route('/proxy/getOwnReqs', methods=['GET'])(getOwnReqsEntry)
        self.app.route('/proxy/getLikes', methods=['GET'])(getLikesEntry)
        self.app.route('/proxy/getAllReqs', methods=['GET'])(getAllReqsEntry)
        self.app.route('/proxy/getRequest', methods=['GET'])(getRequestEntry)
        self.app.route('/proxy/getFeed', methods=['GET'])(getFeedEntry)
        self.app.route('/proxy/nbUser', methods=['GET'])(self.nbUser)
        self.app.route('/proxy/getMsgs', methods=['GET'])(getMsgsEntry)
        self.app.route('/proxy/getInterressed',
                       methods=['GET'])(getInterressedEntry)
        self.app.route('/proxy/getGraphqlUser',
                       methods=['GET'])(getGraphqlUserEntry)
        self.app.route('/proxy/isBlocked', methods=['GET'])(isBlockedEntry)

        self.app.route('/proxy/postReq', methods=['POST'])(postReqEntry)
        self.app.route('/proxy/visible', methods=['POST'])(visibleEntry)
        self.app.route('/proxy/postNotifToken',
                       methods=['POST'])(postNotifTokenEntry)
        self.app.route('/proxy/postPP', methods=['POST'])(postPPEntry)
        self.app.route('/proxy/postPPSetting',
                       methods=['POST'])(postPPSettingEntry)
        self.app.route('/proxy/postName', methods=['POST'])(postNameEntry)
        self.app.route('/proxy/postGraphqlUser',
                       methods=['POST'])(postGraphqlUserEntry)
        self.app.route('/proxy/onConnection',
                       methods=['POST'])(self.onConnectionEntry)
        self.app.route('/proxy/onDisconnection',
                       methods=['POST'])(self.onDisconnectionEntry)
        self.app.route('/proxy/deleteReq', methods=['POST'])(deleteReqEntry)
        self.app.route('/proxy/postComments',
                       methods=['POST'])(postCommentsEntry)
        self.app.route('/proxy/likeReq', methods=['POST'])(likeReqEntry)
        self.app.route('/proxy/deleteAccount',
                       methods=['POST'])(deleteAccountEntry)
        self.app.route('/proxy/signal_request', methods=['POST'])(signalEntry)
        self.app.route('/proxy/sendMsg', methods=['POST'])(sendMsgEntry)
        self.app.route('/proxy/connect', methods=['POST'])(connectEntry)
        self.app.route('/proxy/deleteMsgs', methods=['POST'])(deleteMsgsEntry)
        self.app.route('/proxy/deleteMsg', methods=['POST'])(deleteMsgEntry)
        self.app.route('/proxy/deleteInterressed',
                       methods=['POST'])(deleteInterressedEntry)
        self.app.route('/proxy/blockUser', methods=['POST'])(blockUserEntry)
        self.app.route('/proxy/postLocation',
                       methods=['POST'])(postLocationEntry)
        self.app.route('/proxy/signUp', methods=['POST'])(signUpEntry)
        self.app.route('/proxy/refreshToken', methods=['POST'])(refreshEntry)
        # Stream
        self.app.route('/proxy/stream/<path:subpath>',
                       methods=['GET'])(stream_file)

        # Preview
        self.app.route('/proxy/preview', methods=['GET'])(previewEntry)

        # Analyzer
        self.app.route('/proxy/getBots', methods=['GET'])(getBotsEntry)
        self.app.route('/proxy/scanRequests',
                       methods=['GET'])(scanRequestsEntry)
        self.app.route('/proxy/hashGetAll', methods=['GET'])(hashGetAllEntry)

        self.app.route('/proxy/createBot', methods=['POST'])(createBotEntry)
        self.app.route('/proxy/postBotInfos',
                       methods=['POST'])(postBotInfosEntry)
        self.app.route('/proxy/deleteHash', methods=['POST'])(deleteHashEntry)

    def onConnectionEntry(self):
        try:
            request = flask.request
            request_json = request.get_json()
            id = request_json['id']
            self.user_connected += 1
            return onConnection(id)
        except Exception as e:
            logger.critical("proxy onConnectionEntry args error: " + str(e))
            return {}

    def onDisconnectionEntry(self):
        try:
            request = flask.request
            request_json = request.get_json()
            id = request_json['id']
            self.user_connected -= 1
            return onDisconnection(id)
        except Exception as e:
            logger.critical("proxy onDisconnectionEntry args error: " + str(e))
            return {}

    def nbUser(self):
        try:
            return {'nbuser': self.user_connected}
        except Exception as e:
            logger.critical("proxy onDisconnectionEntry args error: " + str(e))
            return {}

    def run(self):
        # HTTPS
        # app.run(ssl_context=(self.certfile, self.keyfile), host='0.0.0.0', port=self.port, debug="on")
        # HTTP
        if mode == "test":
            print('run proxy in MODE test')
            self.app.run(host='0.0.0.0', port=8000, debug=True)
        else:
            self.app.run(host='0.0.0.0', port=8000, debug=False)


if mode != "test":
    proxy = Proxy()
    app = proxy.app
