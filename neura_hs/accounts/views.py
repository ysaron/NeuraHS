from django.contrib.auth import views as auth_views
from django.contrib.auth import logout, login
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from .forms import RegisterUserForm, LoginUserForm, ChangePasswordForm
from utils.mixins import DataMixin


class SignUp(DataMixin, generic.CreateView):
    """ Создание нового пользователя """
    form_class = RegisterUserForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:signin')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        default_context = self.get_custom_context(title="Регистрация")
        context |= default_context
        return context

    def form_valid(self, form):
        """ Метод, вызываемый после успешной проверки формы """

        user = form.save()

        user.refresh_from_db()  # обновление объекта Юзера для захвата связанного экземпляра Автора

        # Ручное сохранения данных для полей расширяющей модели
        user.author.about = form.cleaned_data.get('about')

        # Присваивание групп и разрешений по умолчанию
        group = Group.objects.get(name='common')
        user.groups.add(group)

        login(self.request, user)   # Автоматическая авторизация после регистрации
        return redirect('gallery:index')


class SignIn(DataMixin, auth_views.LoginView):
    """ Авторизация зарегистрированного пользователя """
    form_class = LoginUserForm
    template_name = 'accounts/signin.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        default_context = self.get_custom_context(title='Авторизация')
        context |= default_context
        return context

    def get_success_url(self):
        if next_url := self.request.GET.get('next'):
            return next_url
        return reverse_lazy('home')


def signout_user(request):
    """ функция отображения для выхода из учетной записи """
    logout(request)
    return redirect(reverse_lazy('accounts:signin'))


class ChangePassword(DataMixin, auth_views.PasswordResetView):
    """  """
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:change_password_emailed')

    form_class = ChangePasswordForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        default_context = self.get_custom_context(title='Смена пароля', label='Адрес электронной почты:')
        context |= default_context
        return context


class ChangePasswordEmailed(DataMixin, auth_views.PasswordResetDoneView):
    """  """
    template_name = 'accounts/password_reset_done.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        default_context = self.get_custom_context(title='Проверьте электронную почту')
        context |= default_context
        return context


class ChangePasswordConfirm(DataMixin, auth_views.PasswordResetConfirmView):
    """  """
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:change_password_complete')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        default_context = self.get_custom_context(title='Новый пароль')
        context |= default_context
        return context


class ChangePasswordComplete(DataMixin, auth_views.PasswordResetCompleteView):
    """  """
    template_name = 'accounts/password_reset_complete.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        default_context = self.get_custom_context(title='Пароль изменен')
        context |= default_context
        return context




