from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db import models

class UserProfileManager(BaseUserManager):
    """Custom manager where email is the unique identifier for authentication."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class UserProfile(AbstractUser):
    class Role(models.IntegerChoices):
        ADMIN = 0, _('Administrator')
        TEACHER = 1, _('Teacher')
        STUDENT = 2, _('Student')

    username = None  # Отключаем использование username
    email = models.EmailField(_("email address"), unique=True)
    email_verify = models.BooleanField(_("email verify"), default=False)
    role = models.IntegerField(verbose_name=_("Role"), choices=Role.choices, default=Role.STUDENT)
    telegram = models.CharField(verbose_name=_("Telegram"), max_length=128, blank=True)
    avatar = models.ImageField(verbose_name=_("Avatar"), upload_to='avatar/', blank=True, default='avatar/default.png')

    USERNAME_FIELD = 'email'  # Определяем email как основной для входа
    REQUIRED_FIELDS = []  # Убираем обязательное поле username

    objects = UserProfileManager()  # Связываем с кастомным менеджером


    def __str__(self):
        return f'{self.email}'  # Используем email для отображения

    def set_active(self, is_active=True):
        self.is_active = is_active
        self.save()

    def restore(self):
        self.set_active(True)

    def delete(self, using=None, keep_parents=False):
        self.set_active(False)