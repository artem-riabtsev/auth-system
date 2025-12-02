from django.conf import settings
from django.db.models import Q

from .models import AccessRule, BusinessElement, PermissionType, Role


class PermissionChecker:
    """Класс для проверки прав доступа пользователя"""

    @staticmethod
    def get_user_roles(user):
        """Получить все роли пользователя"""
        if not user or not user.is_authenticated:
            return Role.objects.filter(name="Гость")

        return user.roles.all()

    @staticmethod
    def has_permission(user, element_code, permission_code, object_owner_id=None):
        if not user or not user.is_authenticated:
            return False

        roles = PermissionChecker.get_user_roles(user)
        if not roles:
            return False

        try:
            element = BusinessElement.objects.get(code=element_code)
            permission_type = PermissionType.objects.get(code=permission_code)
        except (BusinessElement.DoesNotExist, PermissionType.DoesNotExist):
            return False

        rules = AccessRule.objects.filter(
            role__in=roles, element=element, permission_type=permission_type
        )

        for rule in rules:
            if rule.scope == "ALL":
                return True
            elif rule.scope == "OWN" and object_owner_id and user.id == object_owner_id:
                return True

        return False

    @staticmethod
    def get_user_permissions(user):
        permissions = {}
        roles = PermissionChecker.get_user_roles(user)

        for role in roles:
            rules = AccessRule.objects.filter(role=role).select_related(
                "element", "permission_type"
            )
            for rule in rules:
                element_code = rule.element.code
                perm_code = rule.permission_type.code

                if element_code not in permissions:
                    permissions[element_code] = {}

                current_scope = permissions[element_code].get(perm_code, "NONE")

                if rule.scope == "ALL" or (
                    rule.scope == "OWN" and current_scope != "ALL"
                ):
                    permissions[element_code][perm_code] = rule.scope

        return permissions


# УПРОЩЕННЫЙ декоратор без ошибок
def check_permission(element_code, permission_code):
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            from permissions.utils import PermissionChecker

            has_perm = PermissionChecker.has_permission(
                user=request.user,
                element_code=element_code,
                permission_code=permission_code,
            )

            if not has_perm:
                from rest_framework import status
                from rest_framework.response import Response

                return Response(
                    {"detail": "У вас нет прав для выполнения этого действия"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            return view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator
