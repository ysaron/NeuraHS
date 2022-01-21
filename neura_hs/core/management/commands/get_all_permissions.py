from django.core.management.base import BaseCommand
from django.contrib import auth


class Command(BaseCommand):

    help = 'Get a list of all permissions available in the system.'

    def handle(self, *args, **options):
        permissions = set()

        # Создание временного суперюзера (без сохранения) для получения всех разрешений
        temp_superuser = auth.get_user_model()(is_active=True, is_superuser=True)

        # Просмотр каждого AUTHENTICATION_BACKEND и обновление списка разрешений
        for backend in auth.get_backends():
            if hasattr(backend, 'get_all_permissions'):
                permissions |= backend.get_all_permissions(temp_superuser)

        # Получение отсортированного списка разрешений
        permission_list = sorted(list(permissions))

        # Вывод списка в командной строке
        self.stdout.write('\n'.join(permission_list))
