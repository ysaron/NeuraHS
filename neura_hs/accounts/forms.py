from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings


class RegisterUserForm(auth_forms.UserCreationForm):

    # Переопределение стандартных полей для назначения стилей оформления
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    about = forms.CharField(label='О себе', required=False,
                            widget=forms.Textarea(attrs={'cols': 30, 'rows': 6, 'class': 'form-input no-resize'}))

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email']
        if email != settings.TEST_EMAIL and User.objects.filter(email=email).exists():
            raise ValidationError(f'Email {email} уже зарегистрирован.')
        return email


class LoginUserForm(auth_forms.AuthenticationForm):
    """ Изменение дефолтной формы авторизации для улучшения ее отображения """

    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
