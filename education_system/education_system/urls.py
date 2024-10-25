from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authapp.urls', namespace='auth')),
    path('chat/', include('chatapp.urls', namespace='chat')),
    path('teacher/', include('teacher.urls', namespace='teacher')),
    path('', include('mainapp.urls', namespace='main')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
