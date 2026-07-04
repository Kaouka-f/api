import os
from firebase_admin import credentials, messaging
import firebase_admin

def delete_fcm_instance(fcm_token):
    try:
        # Deletes the app instance associated with the provided FCM token
        firebase_admin.messaging.delete_instance_id(fcm_token)
        print(f"Successfully deleted the app instance with token: {fcm_token}")
    except Exception as e:
        print(f"Error deleting the app instance: {e}")

def sendNotif(notifToken, title, message, badge=1, image_url=None):
    try:
        app_name = f"firebase_app_{os.getpid()}"
        app = firebase_admin.get_app(app_name)
        notification = messaging.Notification(
            title=title,
            body=message,
            image=image_url  # Set image URL here
        ) if image_url else messaging.Notification(
            title=title,
            body=message
        )
        msg = messaging.Message(
            notification=notification,
            token=notifToken,
            android=messaging.AndroidConfig(priority="high"),
            apns=messaging.APNSConfig(
                headers={
                    'apns-priority': '10',
                    'apns-push-type': 'alert',
                    'apns-topic': 'com.elab.kaouka'
                },
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        alert=messaging.ApsAlert(
                            title=title,
                            body=message
                        ),
                        content_available=True,
                        badge=badge,
                        sound='default',
                        mutable_content=True,
                        category="rich-apns"
                    ),
                ),
            ),
        )
        id = messaging.send(msg, app=app)
        return id
    except Exception as e:
        return str(e)

