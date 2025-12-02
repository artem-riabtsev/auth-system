from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


class PermissionMiddleware(MiddlewareMixin):
    """
    Middleware для возврата 401 ошибки при отсутствии аутентификации
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Проверяем, требуется ли аутентификация для этого view
        if hasattr(view_func, "cls"):
            view_class = view_func.cls
            if hasattr(view_class, "permission_classes"):
                from rest_framework.permissions import IsAuthenticated

                permission_classes = view_class.permission_classes

                # Проверяем, требует ли view аутентификации
                requires_auth = any(
                    perm == IsAuthenticated
                    or (isinstance(perm, type) and issubclass(perm, IsAuthenticated))
                    for perm in permission_classes
                )

                if requires_auth and not request.user.is_authenticated:
                    return JsonResponse(
                        {"detail": "Требуется аутентификация"}, status=401
                    )

        return None
