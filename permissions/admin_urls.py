from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .admin_views import (AccessRuleViewSet, BusinessElementViewSet,
                          PermissionTypeViewSet, RoleViewSet)

router = DefaultRouter()
router.register(r"roles", RoleViewSet, basename="admin-role")
router.register(r"elements", BusinessElementViewSet, basename="admin-element")
router.register(
    r"permission-types", PermissionTypeViewSet, basename="admin-permission-type"
)
router.register(r"rules", AccessRuleViewSet, basename="admin-rule")

urlpatterns = [
    path("", include(router.urls)),
]
