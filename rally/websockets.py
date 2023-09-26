import asyncio
import json
from urllib.parse import parse_qs

from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer

from .models import Group
from .views import render_track_element
from .track_controller import track_controller


class GroupConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        group_id = parse_qs(self.scope["query_string"].decode("utf8"))["group_id"][0]
        self.group = await asyncio.to_thread(lambda: Group.objects.get(public_id=group_id))
        await self.channel_layer.group_add(group_id, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group.public_id, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        next_element_or_error = await asyncio.to_thread(lambda: track_controller.process_answer(
            text_data_json["element_id"], self.group, text_data_json.get("answer")))
        if isinstance(next_element_or_error, str):
            await self.send(text_data='<h4 id="error" hx-swap-oob="true">' + next_element_or_error + "</h1>")
        else:
            await self.channel_layer.group_send(
                self.group.public_id, {"type": "state.update", "message": render_track_element(next_element_or_error)}
            )

    async def state_update(self, event):
        await self.send(text_data=event["message"])
