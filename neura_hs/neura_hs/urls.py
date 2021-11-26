"""neura_hs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView

from core.views import homepage, about, contact, statistics


urlpatterns = [
    path('', RedirectView.as_view(url='decks/', permanent=True), name='home'),
    path('decks/', include('decks.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('statistics/', statistics, name='statistics'),
    path('i18n/', include('django.conf.urls.i18n')),
]
# приложения, для которых мы хотим делать перевод
urlpatterns += i18n_patterns(
    path('gallery/', include('gallery.urls')),
)


if settings.DEBUG:
    # Подключение статических файлов (локально)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Django Debug Toolbar
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
