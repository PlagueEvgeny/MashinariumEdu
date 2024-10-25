from authapp.models import UserProfile
from mainapp.models import Course
from django.db import models


class Room(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Курс")
    name = models.CharField(max_length=255, verbose_name="Название комнаты")
    slug = models.SlugField(unique=True, verbose_name="Название ссылки для комнаты")
    user = models.ManyToManyField(UserProfile,
                                  related_name='rooms',
                                  related_query_name="room",
                                  blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ["name"]
        verbose_name = "Комната"
        verbose_name_plural = "Комнаты"


class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE, verbose_name="Комната")
    user = models.ForeignKey(UserProfile, related_name='messages', on_delete=models.CASCADE,
                             verbose_name="Пользователь")
    content = models.TextField(verbose_name="Текст сообщения")
    date_added = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")

    def __str__(self):
        return f'{self.room.name}'

    class Meta:
        ordering = ('date_added',)
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
