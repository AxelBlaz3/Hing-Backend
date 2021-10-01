from firebase_admin import messaging
from extensions import NotificationType

class PushNotification:

    @staticmethod
    def send_notification(token: str, image: str):
        try:
            message = messaging.Message(notification=messaging.Notification(image=image), token=token)
            messaging.send(message=message)
        except Exception as e:
            print(e)
            pass    
