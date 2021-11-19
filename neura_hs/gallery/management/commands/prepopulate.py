from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


editor_perms = ['gallery.add_cardclass',
                'gallery.add_cardset',
                'gallery.add_fancard',
                'gallery.add_tribe',
                'gallery.change_fancard',
                'gallery.delete_fancard',
                'gallery.view_author',
                'gallery.view_cardclass',
                'gallery.view_cardset',
                'gallery.view_fancard',
                'gallery.view_realcard',
                'gallery.view_tribe']

common_perms = ['gallery.add_fancard',
                'gallery.view_cardclass',
                'gallery.view_cardset',
                'gallery.view_fancard',
                'gallery.view_realcard',
                'gallery.view_tribe']


class Command(BaseCommand):
    help = 'Prepopulate DB with data necessary for the site to work.'

    def handle(self, *args, **options):
        self.add_user_groups()
        self.stdout.write('Готово')

    def add_user_groups(self):
        editor, created = Group.objects.get_or_create(name='editor')
        msg = 'Создана группа "editor"' if created else 'Группа "editor" уже существует'
        self.stdout.write(msg)
        set_permissions_to_group(editor, editor_perms)
        self.stdout.write('Обновлены разрешения для группы "editor"')

        common, created = Group.objects.get_or_create(name='common')
        msg = 'Создана группа "common"' if created else 'Группа "common" уже существует'
        self.stdout.write(msg)
        set_permissions_to_group(common, common_perms)
        self.stdout.write('Обновлены разрешения для группы "common"')


def set_permissions_to_group(group: Group, permissions: list[str]):
    """  """
    for perm in permissions:
        app, codename = perm.split('.')
        group.permissions.add(Permission.objects.get(content_type__app_label=app, codename=codename))
