"""
WebSocket consumers for real-time chat.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):
    """Real-time chat consumer for a single conversation."""

    async def connect(self):
        self.user = self.scope['user']
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'

        # Reject unauthenticated users
        if self.user.is_anonymous:
            await self.close(code=4001)
            return

        # Verify user is a participant
        is_participant = await self._is_participant()
        if not is_participant:
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Notify others that this user joined (optional presence)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_presence',
                'user_id': self.user.id,
                'username': self.user.username,
                'status': 'online',
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_presence',
                    'user_id': getattr(self.user, 'id', None),
                    'username': getattr(self.user, 'username', ''),
                    'status': 'offline',
                }
            )
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Invalid JSON'}))
            return

        msg_type = data.get('type', 'chat_message')

        if msg_type == 'chat_message':
            content = (data.get('content') or '').strip()
            if not content:
                await self.send(text_data=json.dumps({'type': 'error', 'message': 'Message cannot be empty'}))
                return
            if len(content) > 5000:
                await self.send(text_data=json.dumps({'type': 'error', 'message': 'Message too long'}))
                return

            message = await self._save_message(content)
            if not message:
                await self.send(text_data=json.dumps({'type': 'error', 'message': 'Failed to save message'}))
                return

            # Broadcast to everyone in the room (including sender)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': message['id'],
                        'content': message['content'],
                        'sender_id': message['sender_id'],
                        'sender_username': message['sender_username'],
                        'sender_name': message['sender_name'],
                        'created_at': message['created_at'],
                        'is_read': message['is_read'],
                    },
                }
            )

        elif msg_type == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'is_typing': bool(data.get('is_typing', True)),
                }
            )

        elif msg_type == 'mark_read':
            await self._mark_messages_read()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'messages_read',
                    'user_id': self.user.id,
                    'conversation_id': self.conversation_id,
                }
            )

    # --- Group event handlers ---

    async def chat_message(self, event):
        """Send chat message to WebSocket client."""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
        }))

    async def typing_indicator(self, event):
        """Broadcast typing status (don't echo to sender)."""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing'],
            }))

    async def user_presence(self, event):
        """Notify about online/offline status."""
        if event.get('user_id') != getattr(self.user, 'id', None):
            await self.send(text_data=json.dumps({
                'type': 'presence',
                'user_id': event['user_id'],
                'username': event['username'],
                'status': event['status'],
            }))

    async def messages_read(self, event):
        """Notify that messages were read."""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'messages_read',
                'user_id': event['user_id'],
                'conversation_id': event['conversation_id'],
            }))

    # --- Database helpers ---

    @database_sync_to_async
    def _is_participant(self):
        try:
            conversation = Conversation.objects.get(pk=self.conversation_id)
            return conversation.participants.filter(pk=self.user.pk).exists()
        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def _save_message(self, content):
        try:
            conversation = Conversation.objects.get(pk=self.conversation_id)
            if not conversation.participants.filter(pk=self.user.pk).exists():
                return None

            msg = Message.objects.create(
                conversation=conversation,
                sender=self.user,
                content=content,
            )
            # Touch conversation updated_at
            Conversation.objects.filter(pk=conversation.pk).update(updated_at=timezone.now())

            display_name = (
                f'{self.user.first_name} {self.user.last_name}'.strip()
                or self.user.username
            )
            return {
                'id': msg.id,
                'content': msg.content,
                'sender_id': self.user.id,
                'sender_username': self.user.username,
                'sender_name': display_name,
                'created_at': msg.created_at.strftime('%H:%M'),
                'created_at_iso': msg.created_at.isoformat(),
                'is_read': False,
            }
        except Exception:
            return None

    @database_sync_to_async
    def _mark_messages_read(self):
        Message.objects.filter(
            conversation_id=self.conversation_id,
            is_read=False,
        ).exclude(sender=self.user).update(is_read=True)
