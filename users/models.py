from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import bcrypt
import jwt
from datetime import datetime, timedelta
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    middle_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)
    roles = models.ManyToManyField(
        'permissions.Role',
        related_name='users',
        blank=True,
        verbose_name='Роли'
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    def __str__(self):
        return self.email
    
    def set_password(self, raw_password):
        salt = bcrypt.gensalt()
        self.password = bcrypt.hashpw(raw_password.encode(), salt).decode()
    
    def check_password(self, raw_password):
        if not self.password:
            return False
        return bcrypt.checkpw(raw_password.encode(), self.password.encode())
    
    def delete(self, soft_delete=True, *args, **kwargs):
        if soft_delete:
            self.is_active = False
            self.deleted_at = timezone.now()
            self.save()
        else:
            super().delete(*args, **kwargs)
    
    def generate_tokens(self):
        access_token = self._generate_token('access')
        refresh_token = self._generate_token('refresh')
        return access_token, refresh_token
    
    def _generate_token(self, token_type):
        now = datetime.utcnow()
        expires_at = now + timedelta(
            seconds=settings.JWT_ACCESS_TOKEN_LIFETIME if token_type == 'access' 
            else settings.JWT_REFRESH_TOKEN_LIFETIME
        )
        payload = {
            'user_id': self.id,
            'email': self.email,
            'type': token_type,
            'exp': expires_at,
            'iat': now
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def verify_token(token):
        try:
            return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        except:
            return None