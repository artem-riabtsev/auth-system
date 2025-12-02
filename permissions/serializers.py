from rest_framework import serializers

from .models import AccessRule, BusinessElement, PermissionType, Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class BusinessElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessElement
        fields = "__all__"


class PermissionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionType
        fields = "__all__"


class AccessRuleSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source="role.name", read_only=True)
    element_name = serializers.CharField(source="element.name", read_only=True)
    permission_type_name = serializers.CharField(
        source="permission_type.name", read_only=True
    )

    class Meta:
        model = AccessRule
        fields = "__all__"
        read_only_fields = ("created_at",)
