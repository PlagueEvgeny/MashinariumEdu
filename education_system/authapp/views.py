from django.urls import reverse
from django.contrib import messages, auth
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render, redirect

import logging

from authapp.utility.verify_email import send_email_for_verify

from authapp.forms import LoginForm, RegisterForm, ProfileForm

from authapp.models import UserProfile

logger = logging.getLogger(__name__)

def verify_email(request, uidb64, token):
    try:
        # Декодируем uid пользователя
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserProfile.objects.get(pk=uid)

    except (TypeError, ValueError, OverflowError, UserProfile.DoesNotExist):
        user = None
        logger.warning(f"Invalid UID or user not found for UID: {uidb64}")

    # Проверяем наличие пользователя и токен
    if user is not None and token_generator.check_token(user, token):
        if not user.email_verify:  # Проверяем, что email еще не подтвержден
            user.email_verify = True
            user.save()
            auth.login(request, user)
            messages.success(request, 'Ваш email был успешно подтвержден.')
            logger.info(f"User {user.email} successfully verified their email.")
        else:
            messages.info(request, 'Ваш email уже был подтвержден ранее.')
            logger.info(f"User {user.email} attempted to re-verify their email.")
        return redirect('auth:profile')
    else:
        messages.warning(request, 'Ваша ссылка на верификацию недействительна. Пожалуйста, запросите новую.')
        logger.warning(f"Invalid or expired verification link used by UID: {uidb64}")
        return redirect('auth:profile')


def login(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']  # Получаем email из формы
            password = form.cleaned_data['password']

            # Аутентифицируем пользователя с использованием email
            user = authenticate(request, email=email, password=password)

            if user is not None:
                if not user.is_active:
                    messages.error(request, "Ваш аккаунт деактивирован. Свяжитесь с поддержкой.")
                    logger.warning(f"Deactivated user {user.email} attempted to log in.")
                elif not user.email_verify:
                    messages.error(request, "Ваш аккаунт не верифицирован. Проверьте почту для подтверждения.")
                    logger.warning(f"Unverified user {user.email} attempted to log in.")
                else:
                    auth_login(request, user)
                    logger.info(f"User {user.email} successfully logged in.")
                    return redirect('auth:profile')
            else:
                messages.error(request, "Неправильный email или пароль.")
                logger.warning("Failed login attempt.")
        else:
            messages.error(request, "Форма содержит ошибки, пожалуйста, проверьте данные.")
    else:
        form = LoginForm()

    context = {
        "title": "Авторизация",
        "form": form
    }
    return render(request, 'authapp/login.html', context)


def logout(request):
    auth.logout(request)
    return redirect('auth:login')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)  # Создаем объект пользователя, но пока не сохраняем его
            user.save()

            # Отправляем письмо для подтверждения email
            try:
                send_email_for_verify(request, user)
                messages.warning(request, 'Перейдите на почту и подтвердите регистрацию.')
                logger.info(f"Verification email sent to {user.email}")
            except Exception as e:
                logger.error(f"Error sending verification email: {e}")
                messages.error(request, 'Ошибка при отправке письма для подтверждения.')

            return redirect('auth:profile')
        else:
            messages.error(request, 'Введены неправильные данные. Пожалуйста, проверьте форму.')
            logger.warning('Form validation failed during registration.')
    else:
        form = RegisterForm()

    context = {
        'title': 'Регистрация',
        'form': form,
    }
    return render(request, 'authapp/register.html', context)


@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        # Обработка запроса на повторную отправку письма для верификации
        if "btn_send_verify_email" in request.POST:
            try:
                send_email_for_verify(request, user)
                messages.success(request, 'Вам на почту было отправлено письмо с подтверждением.')
                logger.info(f"Verification email sent to {user.email}")
            except Exception as e:
                messages.error(request, 'Ошибка при отправке письма для подтверждения.')
                logger.error(f"Failed to send verification email to {user.email}: {e}")
            return redirect('auth:profile')

        # Обработка изменения профиля
        email_old = user.email
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            email_new = form.cleaned_data["email"]
            try:
                # Проверка изменения email
                if email_new != email_old:
                    user.email_verify = False
                    form.save()  # Сохраняем изменения профиля
                    send_email_for_verify(request, user)  # Отправляем письмо при изменении email
                    messages.warning(request, 'Email был изменен. Проверьте почту для подтверждения.')
                    logger.info(f"User {user.username} changed email from {email_old} to {email_new}")
                else:
                    form.save()
                    messages.success(request, 'Ваш профиль успешно обновлен.')
                    logger.info(f"User {user.username} updated their profile.")
            except Exception as e:
                messages.error(request, 'Произошла ошибка при сохранении профиля.')
                logger.error(f"Error updating profile for {user.username}: {e}")
            return redirect('auth:profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')

    # Отображение профиля
    else:
        form = ProfileForm(instance=user)

    context = {
        "title": "Профиль",
        "form": form
    }

    return render(request, "authapp/profile.html", context)
