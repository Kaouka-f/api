###########
# METHODS #
###########
# GET
from get.getArrounds import arrounds
from get.getInfos import getInfos
from get.getId import getId
from analyzer.getBots import getBots
from get.getComments import getComments
from get.getOwnReqs import getOwnReqs
from get.getLikes import getLikes
from get.getAllReqs import getAllReqs
from get.getRequest import getRequest
from get.getFeed import getFeed
from get.streamer import stream_file
from get.getMsgs import getMsgs
from get.getInterressed import getInterressed
from get.preview import preview
# POST
from post.postReq import postReq
from post.visible import visible
from analyzer.createBot import createBot
from post.postNotifToken import postNotifToken
from post.postName import postName
from post.postPP import postPP
from post.postPPSetting import postPPSetting
from post.onConnection import onConnection
from post.onDisconnection import onDisconnection
from post.deleteReq import deleteReq
from post.postComments import postComments
from analyzer.postBotInfos import postBotInfos
from post.likeReq import likeReq
from post.deleteAccount import deleteAccount
from post.signal_request import signal
from post.sendMsg import sendMsg
from post.connect import connect
from post.deleteMsgs import deleteMsgs
from post.deleteMsg import deleteMsg
from post.deleteInterressed import deleteInterressed


# test getMsga
# print(getMsgs("5f77823b-a285-4b61-9f49-b4a341d5d259", 0))

# test thumbnail
from helper.media import create_video_thumbnail
file = "/opt/files/df36a9a2-65e6-435c-82d7-3b887f37fb63..mp4"
output = "/opt/files/df36a9a2-65e6-435c-82d7-3b887f37fb63_thumbnail.jpg"
create_video_thumbnail(file, output)

# test likeReq
# from utils import encodeId
# from redisIface import RedisIface
# id = "2eb8a72a-d93b-4c20-88b8-43d5e0a0a737"
# private = "a0198823-aa23-4409-9ec1-45b02127dfb4"
# encoded = encodeId(id, private)
# reqId = "559c2ff3-adc1-44ed-b28d-acbf71e18304"
# likeReq(encoded, reqId)
# redis = RedisIface()
# print(redis.redis_hgetall(reqId))
# print(redis.redis_hget(id, 'requestsOfInterressed'))

# test signal_request
# signal(encoded, reqId)
# print(redis.redis_hget(reqId, 'signals'))