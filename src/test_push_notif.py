from utils import sendNotif, mediaType
import firebase_admin
from firebase_admin import credentials, messaging
import sys
import os
import argparse
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

cred = credentials.Certificate("../src/key/kaouka-460308906bec.json")
firebase_admin.initialize_app(cred)

# Arg parse
parser = argparse.ArgumentParser(description="Test push notif token")
parser.add_argument("notifToken", help="Push Notif Token")

args = parser.parse_args()


message = 'test message'
sendNotif(args.notifToken, "keet", message)
