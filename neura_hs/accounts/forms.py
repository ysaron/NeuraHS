from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.models import User


class RegisterUserForm(auth_forms.UserCreationForm):

    # Переопределение стандартных полей для назначения стилей оформления
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    about = forms.CharField(label='О себе', required=False,
                            widget=forms.Textarea(attrs={'cols': 30, 'rows': 6, 'class': 'form-control no-resize'}))

    class Meta:
        model = User    # связывание формы со стандартной моделью Юзера
        fields = ('email', 'username', 'password1', 'password2')


class LoginUserForm(auth_forms.AuthenticationForm):
    """ Изменение дефолтной формы авторизации для улучшения ее отображения """

    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class ChangePasswordForm(auth_forms.PasswordResetForm):
    """  """

    email = forms.EmailField(label="Email", max_length=254,
                             widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control'}))




