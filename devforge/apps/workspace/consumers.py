import json
from channels.generic.websocket import AsyncWebsocketConsumer

class WorkspaceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.channel_layer is None:
            await self.close()
            return

        if self.scope["user"].is_anonymous:
            await self.close()
            return

        self.workspace_id = self.scope['url_route']['kwargs']['workspace_id']
        self.room_group_name = f'workspace_{self.workspace_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Broadcast user presence (joined)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_presence',
                'action': 'join',
                'username': self.scope['user'].username
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name') and self.channel_layer is not None:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_presence',
                    'action': 'leave',
                    'username': self.scope['user'].username
                }
            )
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        action_type = data.get('type')
        sender_username = self.scope['user'].username

        if action_type == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'workspace_typing',
                    'username': sender_username,
                    'is_typing': data.get('is_typing')
                }
            )
        elif action_type == 'doc_change':
            # Live real-time code collaboration edit sync
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'doc_change',
                    'file_id': data.get('file_id'),
                    'content': data.get('content'),
                    'sender': sender_username
                }
            )
        elif action_type == 'cursor_position':
            # Live multi-user cursor and selection sync
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'cursor_position',
                    'file_id': data.get('file_id'),
                    'cursor': data.get('cursor'),
                    'sender': sender_username,
                    'color': data.get('color', '#38bdf8')
                }
            )

    # Broadcast handlers
    async def workspace_chat(self, event):
        await self.send(text_data=json.dumps(event['data']))

    async def workspace_typing(self, event):
        if event['username'] != self.scope['user'].username:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'username': event['username'],
                'is_typing': event['is_typing']
            }))

    async def doc_change(self, event):
        if event.get('sender') != self.scope['user'].username:
            await self.send(text_data=json.dumps({
                'type': 'doc_change',
                'file_id': event.get('file_id'),
                'content': event.get('content'),
                'sender': event.get('sender')
            }))

    async def cursor_position(self, event):
        if event.get('sender') != self.scope['user'].username:
            await self.send(text_data=json.dumps({
                'type': 'cursor_position',
                'file_id': event.get('file_id'),
                'cursor': event.get('cursor'),
                'sender': event.get('sender'),
                'color': event.get('color')
            }))

    async def user_presence(self, event):
        if event.get('username') != self.scope['user'].username:
            await self.send(text_data=json.dumps({
                'type': 'user_presence',
                'action': event.get('action'),
                'username': event.get('username')
            }))

    async def file_change(self, event):
        if event.get('sender') != self.scope['user'].username:
            await self.send(text_data=json.dumps({
                'type': 'file_change',
                'action': event.get('action'),
                'file_id': event.get('file_id'),
                'name': event.get('name'),
                'path': event.get('path'),
                'sender': event.get('sender')
            }))
