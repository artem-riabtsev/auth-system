from django.conf import settings
from django.db import models


class Role(models.Model):
    """Роли пользователей (админ, менеджер, пользователь, гость)"""

    name = models.CharField(max_length=50, unique=True, verbose_name="Название роли")
    description = models.TextField(blank=True, verbose_name="Описание")
    is_default = models.BooleanField(default=False, verbose_name="Роль по умолчанию")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Если устанавливаем is_default=True для этой роли,
        # снимаем is_default со всех других ролей
        if self.is_default:
            Role.objects.filter(is_default=True).exclude(id=self.id).update(
                is_default=False
            )
        super().save(*args, **kwargs)


class BusinessElement(models.Model):
    """Бизнес-элементы/ресурсы системы"""

    name = models.CharField(max_length=100, verbose_name="Название")
    code = models.CharField(max_length=50, unique=True, verbose_name="Код")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Бизнес-элемент"
        verbose_name_plural = "Бизнес-элементы"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class PermissionType(models.Model):
    """Типы разрешений (read, create, update, delete)"""

    name = models.CharField(max_length=50, verbose_name="Название")
    code = models.CharField(max_length=50, unique=True, verbose_name="Код")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Тип разрешения"
        verbose_name_plural = "Типы разрешений"
        ordering = ["name"]

    def __str__(self):
        return self.name


class AccessRule(models.Model):
    """Правила доступа ролей к элементам"""

    SCOPE_CHOICES = [
        ("NONE", "Нет доступа"),
        ("OWN", "Только свои объекты"),
        ("ALL", "Все объекты"),
    ]

    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="Роль")
    element = models.ForeignKey(
        BusinessElement, on_delete=models.CASCADE, verbose_name="Элемент"
    )
    permission_type = models.ForeignKey(
        PermissionType, on_delete=models.CASCADE, verbose_name="Тип разрешения"
    )
    scope = models.CharField(
        max_length=10,
        choices=SCOPE_CHOICES,
        default="NONE",
        verbose_name="Область действия",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Правило доступа"
        verbose_name_plural = "Правила доступа"
        unique_together = ["role", "element", "permission_type"]
        ordering = ["role", "element"]

    def __str__(self):
        return f"{self.role} → {self.element} ({self.permission_type}): {self.scope}"


class UserRole(models.Model):
    """Связь пользователей с ролями (многие-ко-многим)"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="Роль")
    assigned_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата назначения"
    )

    class Meta:
        verbose_name = "Роль пользователя"
        verbose_name_plural = "Роли пользователей"
        unique_together = ["user", "role"]
        ordering = ["-assigned_at"]

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"
