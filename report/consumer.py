# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LiveUpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Name your channel (e.g., based on model ID if updates are specific to an instance)
        self.group_name = 'live_data'
        
        # Add the channel to a group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the channel from the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive a message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        
        # Send an update to the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'send_live_data',
                'data': data['data']
            }
        )

    # Send live data to WebSocket
    async def send_live_data(self, event):
        await self.send(text_data=json.dumps({
            'data': event['data']
        }))
