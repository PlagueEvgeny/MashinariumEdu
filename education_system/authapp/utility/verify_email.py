from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator as token_generator
import logging

logger = logging.getLogger(__name__)


def send_email_for_verify(request, user):
    try:
        # Получаем текущий сайт
        current_site = get_current_site(request)
        subject = f'Подтверждение email на {current_site.name}'

        # Формируем контекст для письма
        context = {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': token_generator.make_token(user),
        }

        # Генерируем сообщение
        message = render_to_string('authapp/verify_email.html', context)

        # Создаем объект EmailMessage
        email = EmailMessage(
            subject,
            message,
            to=[user.email],
        )

        # Отправляем письмо
        email.send()
        logger.info(f"Verification email sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {e}")
