from django.urls import path
import authapp.views as authapp

app_name = 'authapp'

urlpatterns = [
    path('register/', authapp.register, name='register'),
    path('verify_email/<uidb64>/<token>', authapp.verify_email, name='verify_email'),
    path('login/', authapp.login, name='login'),
    path('logout/', authapp.logout, name='logout'),
    path('profile/', authapp.profile, name='profile'),
]
