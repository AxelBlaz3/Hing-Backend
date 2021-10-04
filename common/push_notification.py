from firebase_admin import messaging
from extensions import NotificationType

class PushNotification:

    @staticmethod
    def send_notification(token: str, image: str, notification_data):
        try:
            message = messaging.Message(data=notification_data, token=token)
            messaging.send(message=message)
        except Exception as e:
            print(e)
            pass    
