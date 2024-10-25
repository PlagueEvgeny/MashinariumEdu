from django.urls import path
import chatapp.views as chatapp

app_name = 'chatapp'

urlpatterns = [
    path("rooms/", chatapp.rooms, name="rooms"),
    path("rooms/<slug:slug>/<str:name>/", chatapp.create_rooms, name="create_rooms"),
    path('rooms/<slug:slug>/', chatapp.room, name='room'),
]
