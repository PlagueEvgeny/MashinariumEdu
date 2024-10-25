import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from authapp.models import UserProfile
from .models import Message, Room


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = 'chat_%s' % self.room_name

            # Присоединение к группе чата
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        except Exception as e:
            print(f"Error during connect: {e}")
            await self.close()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

            # Сохранение сообщения в базу данных
            await self.save_message(
                data['email'],
                data['room'],
                data['message'],
                data['date_added'],
                data['avatar']
            )

            # Отправка сообщения всем пользователям в комнате
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': data['message'],
                    'avatar': data['avatar'],
                    'date_added': data['date_added'],
                    'email': data['email'],
                    'room': data['room'],
                }
            )
        except Exception as e:
            print(f"Error during receive: {e}")

    async def chat_message(self, event):
        try:
            # Отправка сообщения в веб-сокет
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'date_added': event['date_added'],
                'avatar': event['avatar'],
                'email': event['email'],
                'room': event['room'],
            }))
        except Exception as e:
            print(f"Error during chat_message: {e}")

    @sync_to_async
    def save_message(self, email, room_slug, message, date_added, avatar):
        try:
            user = UserProfile.objects.get(email=email)
            room = Room.objects.get(slug=room_slug)

            # Создание нового сообщения
            Message.objects.create(user=user, room=room, content=message, date_added=date_added)
        except UserProfile.DoesNotExist:
            print(f"UserProfile with email {email} does not exist.")
        except Room.DoesNotExist:
            print(f"Room with slug {room_slug} does not exist.")
        except Exception as e:
            print(f"Error during save_message: {e}")
