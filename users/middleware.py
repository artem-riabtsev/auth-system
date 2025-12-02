from django.utils.deprecation import MiddlewareMixin
from .models import User


class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            return
        
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return
        
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != 'bearer':
                return
        except:
            return
        
        payload = User.verify_token(token)
        if not payload or payload.get('type') != 'access':
            return
        
        try:
            user = User.objects.get(id=payload['user_id'], is_active=True)
            request.user = user
        except User.DoesNotExist:
            pass