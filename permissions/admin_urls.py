from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .admin_views import (
    RoleViewSet, 
    BusinessElementViewSet, 
    PermissionTypeViewSet, 
    AccessRuleViewSet
)

router = DefaultRouter()
router.register(r'roles', RoleViewSet, basename='admin-role')
router.register(r'elements', BusinessElementViewSet, basename='admin-element')
router.register(r'permission-types', PermissionTypeViewSet, basename='admin-permission-type')
router.register(r'rules', AccessRuleViewSet, basename='admin-rule')

urlpatterns = [
    path('', include(router.urls)),
]