from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Role, BusinessElement, PermissionType, AccessRule
from .serializers import (
    RoleSerializer, 
    BusinessElementSerializer, 
    PermissionTypeSerializer, 
    AccessRuleSerializer
)
from .utils import PermissionChecker


class IsAdminUser(IsAuthenticated):
    """Проверка что пользователь - администратор"""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        # Проверяем есть ли у пользователя роль "Администратор"
        user_roles = request.user.roles.values_list('name', flat=True)
        return 'Администратор' in user_roles


class RoleViewSet(viewsets.ModelViewSet):
    """Управление ролями (только для администраторов)"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        return Role.objects.all().order_by('name')


class BusinessElementViewSet(viewsets.ModelViewSet):
    """Управление бизнес-элементами (только для администраторов)"""
    queryset = BusinessElement.objects.all()
    serializer_class = BusinessElementSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        return BusinessElement.objects.all().order_by('name')


class PermissionTypeViewSet(viewsets.ModelViewSet):
    """Управление типами разрешений (только для администраторов)"""
    queryset = PermissionType.objects.all()
    serializer_class = PermissionTypeSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        return PermissionType.objects.all().order_by('name')


class AccessRuleViewSet(viewsets.ModelViewSet):
    """Управление правилами доступа (только для администраторов)"""
    queryset = AccessRule.objects.all()
    serializer_class = AccessRuleSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        return AccessRule.objects.select_related(
            'role', 'element', 'permission_type'
        ).order_by('role__name', 'element__name')
    
    @action(detail=False, methods=['get'])
    def by_role(self, request):
        """Получить правила по роли"""
        role_id = request.query_params.get('role_id')
        if not role_id:
            return Response(
                {'error': 'Параметр role_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rules = AccessRule.objects.filter(role_id=role_id).select_related(
            'element', 'permission_type'
        )
        serializer = self.get_serializer(rules, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_element(self, request):
        """Получить правила по элементу"""
        element_id = request.query_params.get('element_id')
        if not element_id:
            return Response(
                {'error': 'Параметр element_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rules = AccessRule.objects.filter(element_id=element_id).select_related(
            'role', 'permission_type'
        )
        serializer = self.get_serializer(rules, many=True)
        return Response(serializer.data)