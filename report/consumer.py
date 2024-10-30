import json
from channels.generic.websocket import AsyncWebsocketConsumer


class LiveUpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        self.group_name = "live_data"

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        await self.channel_layer.group_send(
            self.group_name, {"type": "send_live_data", "data": data["data"]}
        )

    async def send_live_data(self, event):
        await self.send(text_data=json.dumps({"data": event["data"]}))
