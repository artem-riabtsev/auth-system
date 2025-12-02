from django.contrib import admin

from .models import AccessRule, BusinessElement, PermissionType, Role, UserRole


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "is_default", "created_at")
    list_filter = ("is_default", "created_at")
    search_fields = ("name", "description")
    ordering = ("name",)


@admin.register(BusinessElement)
class BusinessElementAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "description", "created_at")
    search_fields = ("name", "code", "description")
    ordering = ("name",)


@admin.register(PermissionType)
class PermissionTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "description")
    search_fields = ("name", "code")
    ordering = ("name",)


@admin.register(AccessRule)
class AccessRuleAdmin(admin.ModelAdmin):
    list_display = ("role", "element", "permission_type", "scope", "created_at")
    list_filter = ("role", "element", "permission_type", "scope")
    search_fields = ("role__name", "element__name", "permission_type__name")
    ordering = ("role", "element")


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "assigned_at")
    list_filter = ("role", "assigned_at")
    search_fields = ("user__email", "role__name")
    raw_id_fields = ("user",)
    ordering = ("-assigned_at",)
