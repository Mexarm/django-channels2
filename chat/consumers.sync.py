import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']

        # Group names are restricted to ASCII alphanumerics,
        # hyphens, and periods only. Since this code constructs
        # a group name directly from the room name,
        # it will fail if the room name contains any characters
        # that aren’t valid in a group name.
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        # Accepts the WebSocket connection.
        # If you do not call accept() within the connect()
        # method then the connection will be rejected and closed.
        # You might want to reject a connection for example
        # because the requesting user is not authorized to perform
        # the requested action.
        # It is recommended that accept() be called as the last
        # action in connect() if you choose to accept the connection.
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group

        # An event has a special 'type' key corresponding
        # to the name of the method that should be invoked
        # on consumers that receive the event.
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
