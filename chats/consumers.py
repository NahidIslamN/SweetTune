import json
import base64
from urllib.parse import parse_qs, urlparse

import jwt

from django.conf import settings
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async as _database_sync_to_async
from django.core.files.base import ContentFile
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Chat, Message, MessageFiles
from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer


# sent notification to user
class NotificationConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        user = self.scope.get("user")
        headers = {k.decode(): v.decode() for k, v in self.scope.get("headers", [])}
        origin = headers.get("origin")
        if origin:
            try:
                host = urlparse(origin).hostname
            except Exception:
                host = None
            allowed = settings.ALLOWED_HOSTS or []
            if allowed != ["*"] and host and host not in allowed:
                await self.close()  # reject cross-origin
                return

        token = None
        qs = self.scope.get("query_string", b"").decode()
        if qs:
            token = parse_qs(qs).get("token", [None])[0]
        if not token:
            auth_header = headers.get("authorization")
            if auth_header and auth_header.lower().startswith("bearer "):
                token = auth_header.split(None, 1)[1]

        if user.is_anonymous or token is None:
            await self.send({"type": "websocket.close", "code": 4001})
            return

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.SIMPLE_JWT.get("ALGORITHM", "HS256")])
        except Exception:
            await self.send({"type": "websocket.close", "code": 4001})
            return

        token_user_id = payload.get("user_id") or payload.get("user")
        # normalize id to int when possible
        try:
            token_user_id_int = int(token_user_id) if token_user_id is not None else None
        except Exception:
            token_user_id_int = None

        # if scope user is anonymous but token valid, load user from DB
        if getattr(user, "is_anonymous", True) and token_user_id_int:
            try:
                user_obj = await _database_sync_to_async(get_user_model().objects.get)(id=token_user_id_int)
            except Exception:
                await self.send({"type": "websocket.close", "code": 4001})
                return
            # inject into scope for downstream code
            self.scope["user"] = user_obj
            user = user_obj

        if not token_user_id_int or getattr(user, "id", None) != token_user_id_int:
            await self.send({"type": "websocket.close", "code": 4001})
            return

        # accepted
        self.room_group_name = f"notification_{user.id}"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.send({
            "type": "websocket.accept"
        })

    async def websocket_receive(self, event):

        text_data = event['text']
        try:
            message = json.loads(text_data)
        except json.JSONDecodeError:
            message = {"text": text_data}

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "sent.note",
                "message": message,
            }
        )

    async def sent_note(self, event):
        data = event['message']
        user = self.scope.get("user")
      
        if not event.get('saved', False):
            await self.save_notification(user=user, data=data)

        await self.send({
            "type": "websocket.send",
            "text": json.dumps(event['message']),
        })

    async def success(self, event):
        await self.sent_note(event)

    async def warning(self, event):
        await self.sent_note(event)

    async def normal(self, event):
        await self.sent_note(event)

    @database_sync_to_async
    def save_notification(self, user, data):
        from .models import NoteModel
        
        return NoteModel.objects.create(
            user=user,
            title=data.get('title'),
            content=data.get('content'),
            note_type = data.get('note_type')
        )

    async def websocket_disconnect(self, event):
        # only discard if room_group_name was set during connect
        if hasattr(self, 'room_group_name') and getattr(self, 'channel_layer', None):
            try:
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
            except Exception:
                pass
        raise StopConsumer()
    


class UpdateChatConsumerMessageGet(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        # verify origin header against ALLOWED_HOSTS
        headers = {k.decode(): v.decode() for k, v in self.scope.get("headers", [])}
        origin = headers.get("origin")
        if origin:
            try:
                host = urlparse(origin).hostname
            except Exception:
                host = None
            allowed = settings.ALLOWED_HOSTS or []
            if allowed != ["*"] and host and host not in allowed:
                await self.close(code=4002)
                return

        # re-validate token
        token = None
        qs = self.scope.get("query_string", b"").decode()
        if qs:
            token = parse_qs(qs).get("token", [None])[0]
        if not token:
            auth_header = headers.get("authorization")
            if auth_header and auth_header.lower().startswith("bearer "):
                token = auth_header.split(None, 1)[1]

        if not self.user or getattr(self.user, "is_anonymous", True) or token is None:
            await self.close(code=4001)
            return

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.SIMPLE_JWT.get("ALGORITHM", "HS256")])
        except Exception:
            await self.close(code=4001)
            return

        token_user_id = payload.get("user_id") or payload.get("user")
        try:
            token_user_id_int = int(token_user_id) if token_user_id is not None else None
        except Exception:
            token_user_id_int = None

        # if scope user is anonymous but token valid, load user from DB
        if getattr(self.user, "is_anonymous", True) and token_user_id_int:
            try:
                user_obj = await _database_sync_to_async(get_user_model().objects.get)(id=token_user_id_int)
            except Exception:
                await self.close(code=4001)
                return
            self.scope["user"] = user_obj
            self.user = user_obj

        if not token_user_id_int or getattr(self.user, "id", None) != token_user_id_int:
            await self.close(code=4001)
            return
        
        self.user_group = f"chats_{self.user.id}"
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # guard in case connect failed before `user_group` was set
        if hasattr(self, 'user_group') and getattr(self, 'channel_layer', None):
            try:
                await self.channel_layer.group_discard(self.user_group, self.channel_name)
            except Exception:
                pass

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except Exception:
            return

        message_text = data.get("message", "")
        chat_id = data.get("chat_id")
        files_data = data.get("files", []) 
        if not chat_id or (not message_text and not files_data):
            return

      
        try:
            message_obj = await self.save_message_to_database(message_text, files_data, chat_id)
        except Exception:
            return

        files_urls = await self.get_message_files(message_obj)

        username = getattr(self.user, "username", None) or getattr(self.user, "email", "Anonymous")
        profile_image = None
        try:
            if getattr(self.user, "image", None):
                profile_image = self.user.image.url
        except Exception:
            profile_image = None

        payload = {
            "id": message_obj.id,
            "text": message_obj.text,
            "status": getattr(message_obj, "status", None),
            "chat_id": chat_id,
            "sender": {"id": self.user.id, "username": username, "profile_image": profile_image},
            "last_activity": str(getattr(self.user, "last_activity", None)),
            "files": files_urls,
            "created_at": message_obj.created_at.isoformat() if message_obj.created_at else None
        }

        # broadcast to each participant's personal group (non-blocking)
        participant_ids = await self.get_chat_participants(chat_id)
        for pid in participant_ids:
            await self.channel_layer.group_send(
                f"chats_{pid}",
                {"type": "chat_message", "message": payload}
            )

    async def chat_message(self, event):
        msg = event.get("message", {})
        await self.send(text_data=json.dumps({
            "success": True,
            "message": msg,
            "chat_id": msg.get("chat_id"),
            "username": (msg.get("sender") or {}).get("username"),
            "image": (msg.get("sender") or {}).get("profile_image"),
            "last_activity": msg.get("last_activity"),
            "files": msg.get("files", [])
        }))

    @database_sync_to_async
    def get_message_files(self, message_obj):
        return [f.file.url for f in message_obj.files.all()]

    @database_sync_to_async
    def save_message_to_database(self, message_text, files, chat_id):
        chat = Chat.objects.get(id=chat_id)
        msg_obj = Message.objects.create(chat=chat, sender=self.user, text=message_text or None)
        for f in files:
            title = f.get("title", "")
            file_base64 = f.get("file_base64")
            if file_base64:
                format_part, imgstr = file_base64.split(';base64,')
                ext = format_part.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name=f"{title}.{ext}")
                file_obj = MessageFiles.objects.create(title=title, file=data)
                msg_obj.files.add(file_obj)
        chat.save()
        return msg_obj

    @database_sync_to_async
    def get_chat_participants(self, chat_id):
        chat = Chat.objects.get(id=chat_id)
        return list(chat.participants.values_list("id", flat=True))

