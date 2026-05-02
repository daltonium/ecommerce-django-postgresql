import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """
    AsyncWebsocketConsumer = base class for async WebSocket handling.

    WHY async?
    ──────────
    WebSocket connections are long-lived and concurrent.
    Synchronous Django views block a thread per request — fine for HTTP.
    But 1000 open WebSocket connections = 1000 blocked threads.
    Async lets one thread handle thousands of connections via event loop.
    """

    async def connect(self):
        """
        Called when a client opens a WebSocket connection.
        ws://localhost:8000/ws/chat/<conversation_id>/
        """
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        # scope = WebSocket equivalent of request. Contains URL params, user, headers.
        # url_route['kwargs'] = URL parameters from the WebSocket URL pattern.

        self.room_group_name = f'chat_{self.conversation_id}'
        # room_group_name = the Redis channel group name.
        # All users in this conversation subscribe to this group.
        # When a message is sent, it's broadcast to ALL members of this group.

        # Verify the user is authenticated
        if self.scope['user'].is_anonymous:
            await self.close()
            return

        # Verify this user is part of this conversation
        is_participant = await self.is_conversation_participant()
        if not is_participant:
            await self.close()
            return

        # Join the Redis channel group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
            # channel_name = unique ID for THIS specific WebSocket connection
            # group_add: "add this connection to the group"
            # Now any message sent to the group reaches this connection.
        )

        await self.accept()
        # accept() = complete the WebSocket handshake. Connection is now open.

    async def disconnect(self, close_code):
        """Called when the WebSocket closes (user navigates away, etc.)"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
            # group_discard: remove this connection from the group.
            # Important: without this, the group accumulates dead connections.
        )

    async def receive(self, text_data):
        """
        Called when the CLIENT sends a message over the WebSocket.
        text_data = the raw string the client sent (JSON format).
        """
        data = json.loads(text_data)
        message_content = data.get('message', '').strip()

        if not message_content:
            return

        # Save to DB (async-safe via database_sync_to_async)
        message = await self.save_message(message_content)

        # Broadcast to ALL users in this conversation's group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                # 'type' maps to the method name below (chat_message).
                # Django Channels calls the method matching this type
                # on every consumer in the group.
                'message': message_content,
                'sender_email': self.scope['user'].email,
                'sender_id': self.scope['user'].id,
                'message_id': message.id,
                'timestamp': message.created_at.isoformat(),
            }
        )

    async def chat_message(self, event):
        """
        Called by group_send when type='chat_message'.
        This runs on EVERY consumer in the group — i.e., every connected user.
        It sends the message DOWN to each client's WebSocket.
        """
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_email': event['sender_email'],
            'sender_id': event['sender_id'],
            'message_id': event['message_id'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def save_message(self, content):
        """
        WHY database_sync_to_async?
        ─────────────────────────────
        Django's ORM is synchronous (blocking DB calls).
        Our consumer is async — you cannot call sync code directly
        in an async function (it would block the event loop).
        database_sync_to_async wraps the sync DB call in a thread pool,
        letting the event loop continue handling other connections.
        """
        conversation = Conversation.objects.get(id=self.conversation_id)
        return Message.objects.create(
            conversation=conversation,
            sender=self.scope['user'],
            content=content
        )

    @database_sync_to_async
    def is_conversation_participant(self):
        """Check if the connecting user belongs to this conversation."""
        user = self.scope['user']
        return Conversation.objects.filter(
            id=self.conversation_id,
            # User must be either the buyer OR the seller
        ).filter(
            models.Q(buyer=user) | models.Q(seller=user)
        ).exists()

# Import at the bottom to avoid circular import
import django.db.models as models