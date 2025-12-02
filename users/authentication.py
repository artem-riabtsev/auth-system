from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != 'bearer':
                raise AuthenticationFailed('Неверный формат токена')
        except:
            raise AuthenticationFailed('Неверный заголовок Authorization')
        
        payload = User.verify_token(token)
        if not payload or payload.get('type') != 'access':
            raise AuthenticationFailed('Неверный или истекший токен')
        
        try:
            user = User.objects.get(id=payload['user_id'], is_active=True)
        except User.DoesNotExist:
            raise AuthenticationFailed('Пользователь не найден')
        
        return (user, token)