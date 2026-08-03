import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .views import Message, Conversation
from apps.accounts.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.channel_layer is None:
            await self.close()
            return

        if self.scope["user"].is_anonymous:
            await self.close()
            return

        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # Receive message from WebSocket (for typing indicators etc.)
    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_typing',
                    'username': self.scope['user'].username,
                    'is_typing': data.get('is_typing')
                }
            )

    # Receive message from room group (broadcast from view or other consumer)
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['data']))

    # Broadcast typing status
    async def chat_typing(self, event):
        if event['username'] != self.scope['user'].username:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'username': event['username'],
                'is_typing': event['is_typing']
            }))
