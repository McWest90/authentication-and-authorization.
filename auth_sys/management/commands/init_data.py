from django.core.management.base import BaseCommand
from auth_sys.models import Role, Resource, Permission, CustomUser
from auth_sys.utils import hash_password

class Command(BaseCommand):
    help = 'Заполняет БД начальными данными (Роли, Ресурсы, Админ)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Начинаю инициализацию данных...")

        # 1. Создаем Роли
        admin_role, _ = Role.objects.get_or_create(slug='admin', defaults={'name': 'Administrator'})
        user_role, _ = Role.objects.get_or_create(slug='user', defaults={'name': 'Regular User'})
        
        self.stdout.write(f"Роли созданы: {admin_role}, {user_role}")

        # 2. Создаем Ресурсы (например, Отчеты)
        res_reports, _ = Resource.objects.get_or_create(
            code='reports', 
            defaults={'description': 'Financial Reports'}
        )
        self.stdout.write(f"Ресурс создан: {res_reports.code}")

        # 3. Раздаем права (Permissions)
        
        # Админ может всё с отчетами
        Permission.objects.get_or_create(
            role=admin_role, 
            resource=res_reports,
            defaults={
                'can_create': True,
                'can_read': True,
                'can_update': True,
                'can_delete': True
            }
        )

        # Обычный юзер может только читать отчеты
        Permission.objects.get_or_create(
            role=user_role, 
            resource=res_reports,
            defaults={
                'can_create': False,
                'can_read': True,
                'can_update': False,
                'can_delete': False
            }
        )
        self.stdout.write("Права назначены.")

        # 4. Создаем Супер-Админа (чтобы можно было залогиниться сразу)
        if not CustomUser.objects.filter(email='admin@example.com').exists():
            CustomUser.objects.create(
                full_name='Super Admin',
                email='admin@example.com',
                password_hash=hash_password('admin123'), # Пароль: admin123
                role=admin_role
            )
            self.stdout.write("Пользователь admin@example.com создан (пароль: admin123)")
        else:
            self.stdout.write("Пользователь admin уже существует.")

        self.stdout.write(self.style.SUCCESS('Инициализация успешно завершена!'))