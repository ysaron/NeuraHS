from django.contrib.auth import views as auth_views
from django.contrib.auth import logout, login
from django.contrib.auth.models import User, Group
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import generic
from django.conf import settings

from .forms import RegisterUserForm, LoginUserForm, ChangePasswordForm
from utils.mixins import DataMixin
from .tokens import account_activation_token


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

    def form_valid(self, form):     # вызывается после успешной проверки формы
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        site = get_current_site(self.request)
        mail_subject = 'Активация аккаунта NeuraHS'
        message = render_to_string(template_name='accounts/acc_active_email.html',
                                   context={'user': user,
                                            'domain': site.domain,
                                            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                            'token': account_activation_token.make_token(user)})
        to_email = form.cleaned_data.get('email')
        email = EmailMessage(subject=mail_subject,
                             body=message, to=[to_email])
        email.content_subtype = 'html'
        email.send()

        user.refresh_from_db()  # обновление объекта User для захвата связанного экземпляра Author

        # Ручное сохранения данных для полей расширяющей модели
        user.author.about = form.cleaned_data.get('about')

        # Присваивание групп и разрешений по умолчанию
        group = Group.objects.get(name='common')
        user.groups.add(group)

        return render(request=self.request,
                      context={'title': 'Проверьте электронную почту',
                               'top_menu': settings.TOP_MENU,
                               'side_menu': settings.SIDE_MENU},
                      template_name='accounts/acc_active_done.html')


def activate(request, uidb64, token):
    """ Активация аккаунта юзера после перехода по ссылке в email """
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request,
                      context={'title': 'Аккаунт активирован',
                               'top_menu': settings.TOP_MENU,
                               'side_menu': settings.SIDE_MENU},
                      template_name='accounts/acc_active_complete.html')
    else:
        return render(request,
                      context={'title': 'Активация провалена',
                               'top_menu': settings.TOP_MENU,
                               'side_menu': settings.SIDE_MENU},
                      template_name='accounts/acc_active_complete.html')


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




