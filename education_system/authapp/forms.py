from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from authapp.models import UserProfile
import django.forms as forms
from django.utils.translation import gettext_lazy as _


class BaseFormMixin:
    """Mixin для общих настроек форм."""
    def add_class_to_fields(self, class_name):
        for name, field in self.fields.items():
            field.widget.attrs['class'] = class_name
            if 'help_text' in field.__dict__:
                field.help_text = f'Введите {_(name)}'


class LoginForm(AuthenticationForm, BaseFormMixin):
    email = forms.EmailField(label=_("Email"), max_length=254)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username')  # Убираем поле username
        self.add_class_to_fields("login__form__{name}")

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            # Здесь используется email для аутентификации
            self.user_cache = UserProfile.objects.get(email=email)
            if self.user_cache.check_password(password):
                return cleaned_data
            else:
                raise forms.ValidationError(_("Invalid email or password."))

        raise forms.ValidationError(_("Please enter both email and password."))



class RegisterForm(UserCreationForm, BaseFormMixin):
    class Meta:
        model = UserProfile
        fields = ('email', 'first_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_class_to_fields('register__form')


class ProfileForm(UserChangeForm, BaseFormMixin):
    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'email', 'telegram', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_class_to_fields('profile__form__{name}')
        # Скрываем поле пароля
        if 'password' in self.fields:
            self.fields['password'].widget = forms.HiddenInput()
