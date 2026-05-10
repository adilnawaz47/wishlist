import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        is_participant = await self.check_participant()
        if not is_participant:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.mark_messages_read()
        await self.channel_layer.group_send(
            self.room_group_name,
            {'type': 'messages_read', 'reader_id': self.user.id}
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_send(
            self.room_group_name,
            {'type': 'webrtc_signal', 'signal': {'type': 'call_end'}, 'sender_id': self.user.id}
        )
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type', 'message')

        if msg_type == 'message':
            content = data.get('content', '').strip()
            if not content:
                return
            message = await self.save_message(content)
            ts = message.timestamp.strftime('%I:%M %p')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_id': message.id,
                    'content': content,
                    'sender_username': self.user.username,
                    'sender_id': self.user.id,
                    'timestamp': ts,
                }
            )

        elif msg_type == 'read':
            await self.mark_messages_read()
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'messages_read', 'reader_id': self.user.id}
            )

        elif msg_type == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'sender_id': self.user.id,
                    'is_typing': data.get('is_typing', False),
                }
            )

        elif msg_type in ('call_offer', 'call_answer', 'ice_candidate', 'call_reject', 'call_end'):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'webrtc_signal',
                    'signal': data,
                    'sender_id': self.user.id,
                    'sender_username': self.user.username,
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message_id': event['message_id'],
            'content': event['content'],
            'sender_username': event['sender_username'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp'],
        }))

    async def messages_read(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read',
            'reader_id': event['reader_id'],
        }))

    async def typing_indicator(self, event):
        if event['sender_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'sender_id': event['sender_id'],
                'is_typing': event['is_typing'],
            }))

    async def webrtc_signal(self, event):
        if event['sender_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                **event['signal'],
                'sender_id': event['sender_id'],
                'sender_username': event.get('sender_username', ''),
            }))

    @database_sync_to_async
    def check_participant(self):
        from .models import Room
        try:
            room = Room.objects.get(id=self.room_id)
            return room.participants.filter(id=self.user.id).exists()
        except Room.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content):
        from .models import Room, Message
        room = Room.objects.get(id=self.room_id)
        return Message.objects.create(room=room, sender=self.user, content=content)

    @database_sync_to_async
    def mark_messages_read(self):
        from .models import Room, Message
        room = Room.objects.get(id=self.room_id)
        Message.objects.filter(room=room, is_read=False).exclude(sender=self.user).update(is_read=True)
