from django.core.management.base import BaseCommand

from permissions.models import (AccessRule, BusinessElement, PermissionType,
                                Role)


class Command(BaseCommand):
    help = "Загружает тестовые данные для системы разрешений"

    def handle(self, *args, **options):
        AccessRule.objects.all().delete()
        PermissionType.objects.all().delete()
        BusinessElement.objects.all().delete()
        Role.objects.all().delete()

        admin_role, _ = Role.objects.get_or_create(
            name="Администратор",
            defaults={
                "description": "Полный доступ ко всем ресурсам",
                "is_default": False,
            },
        )
        manager_role, _ = Role.objects.get_or_create(
            name="Менеджер",
            defaults={
                "description": "Доступ к управлению контентом",
                "is_default": False,
            },
        )
        user_role, _ = Role.objects.get_or_create(
            name="Пользователь",
            defaults={"description": "Обычный пользователь", "is_default": True},
        )
        guest_role, _ = Role.objects.get_or_create(
            name="Гость",
            defaults={"description": "Ограниченный доступ", "is_default": False},
        )

        elements_data = [
            {
                "name": "Пользователи",
                "code": "users",
                "description": "Управление пользователями",
            },
            {
                "name": "Товары",
                "code": "products",
                "description": "Управление товарами",
            },
            {
                "name": "Магазины",
                "code": "stores",
                "description": "Управление магазинами",
            },
            {"name": "Заказы", "code": "orders", "description": "Управление заказами"},
            {
                "name": "Правила доступа",
                "code": "permissions",
                "description": "Управление правами доступа",
            },
        ]

        elements = {}
        for elem_data in elements_data:
            element, _ = BusinessElement.objects.get_or_create(
                code=elem_data["code"], defaults=elem_data
            )
            elements[elem_data["code"]] = element

        permissions_data = [
            {"name": "Чтение", "code": "read", "description": "Просмотр записей"},
            {
                "name": "Создание",
                "code": "create",
                "description": "Создание новых записей",
            },
            {
                "name": "Обновление",
                "code": "update",
                "description": "Изменение существующих записей",
            },
            {"name": "Удаление", "code": "delete", "description": "Удаление записей"},
        ]

        permissions = {}
        for perm_data in permissions_data:
            permission, _ = PermissionType.objects.get_or_create(
                code=perm_data["code"], defaults=perm_data
            )
            permissions[perm_data["code"]] = permission

        for element in elements.values():
            for permission in permissions.values():
                AccessRule.objects.get_or_create(
                    role=admin_role,
                    element=element,
                    permission_type=permission,
                    defaults={"scope": "ALL"},
                )

        for element_code, element in elements.items():
            AccessRule.objects.get_or_create(
                role=manager_role,
                element=element,
                permission_type=permissions["read"],
                defaults={"scope": "ALL"},
            )

            if element_code in ["products", "orders"]:
                for perm_code in ["create", "update"]:
                    AccessRule.objects.get_or_create(
                        role=manager_role,
                        element=element,
                        permission_type=permissions[perm_code],
                        defaults={"scope": "ALL"},
                    )

        user_elements = ["users", "products", "orders"]
        for element_code in user_elements:
            element = elements[element_code]

            AccessRule.objects.get_or_create(
                role=user_role,
                element=element,
                permission_type=permissions["read"],
                defaults={"scope": "OWN"},
            )

            for perm_code in ["create", "update", "delete"]:
                AccessRule.objects.get_or_create(
                    role=user_role,
                    element=element,
                    permission_type=permissions[perm_code],
                    defaults={"scope": "OWN"},
                )

        guest_elements = ["products", "stores"]
        for element_code in guest_elements:
            element = elements[element_code]
            AccessRule.objects.get_or_create(
                role=guest_role,
                element=element,
                permission_type=permissions["read"],
                defaults={"scope": "ALL"},
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Тестовые данные для системы разрешений загружены успешно!"
            )
        )
