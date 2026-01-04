import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

class CrimeAlertConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = 'crime_alerts'
        self.room_group_name = 'crime_alerts'

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        # We don't expect to receive messages from the client in this consumer
        pass

    def send_alert(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
