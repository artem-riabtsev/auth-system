from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .utils import PermissionChecker


class CheckPermissionView(APIView):
    """API для проверки прав пользователя"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        permissions = PermissionChecker.get_user_permissions(request.user)
        user_roles = list(request.user.roles.values_list('name', flat=True))
        
        return Response({
            'user_id': request.user.id,
            'email': request.user.email,
            'roles': user_roles,
            'permissions': permissions
        })


class TestPermissionView(APIView):
    """Тестовый view для проверки конкретного права"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Проверяем право вручную
        has_perm = PermissionChecker.has_permission(
            user=request.user,
            element_code='users',
            permission_code='read'
        )
        
        if not has_perm:
            return Response(
                {'detail': 'У вас нет прав для выполнения этого действия'},
                status=403
            )
        
        return Response({
            'message': 'Доступ разрешен! У вас есть право read на users',
            'user': request.user.email
        })