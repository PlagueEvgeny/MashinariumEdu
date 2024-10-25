from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from chatapp.models import Message, Room
from chatapp.forms import RoomForm


def create_rooms(request, slug, name):
    form = RoomForm(data=request.POST)
    form.name = name
    form.slug = slug
    if form.is_valid():
        form.save()

        return form


@login_required
def rooms(request):
    all_rooms = Room.objects.filter(user=request.user)
    context = {
        "rooms": all_rooms,
        "title": "Доступные чаты"
    }
    return render(request, "chatapp/rooms.html", context)


@login_required
def room(request, slug):
    all_rooms = Room.objects.filter(user=request.user)
    get_room = Room.objects.get(slug=slug)
    message = Message.objects.filter(room=get_room)

    context = {
        'title': get_room.name,
        'rooms': all_rooms,
        'room': get_room,
        'message': message,
    }

    return render(request, "chatapp/room.html", context)
