import json
from urllib.parse import parse_qs

from channels.generic.websocket import WebsocketConsumer

from .models import Group
from .views import render_track_element
from .track_controller import track_controller


class GroupConsumer(WebsocketConsumer):

    def connect(self):
        group_id = parse_qs(self.scope["query_string"].decode("utf8"))["group_id"][0]
        self.group = Group.objects.get(public_id=group_id)
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        next_element_or_error = track_controller.process_answer(text_data_json["element_id"], self.group, text_data_json.get("answer"))
        if isinstance(next_element_or_error, str):
            self.send(text_data='<h4 id="error" hx-swap-oob="true">' + next_element_or_error + "</h1>")
        else:
            self.send(text_data=render_track_element(next_element_or_error))