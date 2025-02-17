import sys
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from firebase_admin import credentials, messaging
import firebase_admin
from src.utils import sendNotif, mediaType

cred = credentials.Certificate("../src/key/kaouka-460308906bec.json")
firebase_admin.initialize_app(cred)

notifToken = "c2sw9ONpSfSkqzgI0JW0jB:APA91bFc_4kdfemS83yFfDWcl60HUIdAMl45BqKsBVR68vQ7YksEmiUdZJ41Ncnsh0-Fp8yTnntGqDVCL0EqKU_r8xTcNKYEQQHdRDt9P-L4QB8STPrjz90"
# notifToken = "ftX89XVVScK0v_thGpHo6u:APA91bGccKME0rn_ZF98iSvJiQk3nrZByQ91jM7irtTO9Wm26Enkg09sSvcv8nRevLLwDJYpKCXsJBBFNx64mdxoEZcfFaR_BrMo_BlzdyQg7csOQdpb-RNSGXwcpUvUPWHYY1GJX45e"

message = 'test message'
sendNotif(notifToken, "keet", message)