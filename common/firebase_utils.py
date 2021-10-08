from typing import List
from firebase_admin import messaging
from firebase_admin.exceptions import FirebaseError
from extensions import NotificationType

class FirebaseUtils:

    @staticmethod
    def send_notification(token: str, image: str, notification_data):
        try:
            message = messaging.Message(data=notification_data, token=token)
            messaging.send(message=message)
        except Exception as e:
            print(e)
            pass    

    @staticmethod
    def subscribe_to_topic(topic: str, tokens: List[str]):
        try:
            messaging.subscribe_to_topic(tokens=tokens, topic=topic)
        except FirebaseError:
            print('Something went wrong with firebase')
        except ValueError:
            print('Input args are invalid')    