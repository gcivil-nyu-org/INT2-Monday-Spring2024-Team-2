from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from TutorRegister.models import ChatSession, Message
from django.contrib.auth.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.other_user_id = self.scope["url_route"]["kwargs"]["user_id"]
        hash_base = "chat"
        sorted_ids = sorted([int(self.scope["user"].id), int(self.other_user_id)])
        self.room_group_name = f"{hash_base}_{sorted_ids[0]}_{sorted_ids[1]}"
        print(self.room_group_name)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        await self.save_message(self.scope["user"].id, self.other_user_id, message)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "author_id": str(self.scope["user"].id),
            },
        )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {"author_id": event["author_id"], "message": event["message"]}
            )
        )

    @database_sync_to_async
    def save_message(self, author_id, other_user_id, message):
        author = User.objects.get(id=author_id)
        other_user = User.objects.get(id=other_user_id)

        chat_session, created = ChatSession.objects.get_or_create(
            tutor=author if author.usertype.user_type == "tutor" else other_user,
            student=author if author.usertype.user_type == "student" else other_user,
        )

        Message.objects.create(
            chat_session=chat_session, author=author, message=message
        )
