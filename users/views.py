from django.contrib.auth import logout
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import (UserLoginSerializer, UserRegistrationSerializer,
                          UserSerializer, UserUpdateSerializer)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            access_token, refresh_token = user.generate_tokens()
            return Response(
                {
                    "user": UserSerializer(user).data,
                    "tokens": {"access": access_token, "refresh": refresh_token},
                    "message": "Регистрация успешна",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            try:
                user = User.objects.get(email=email, is_active=True)
            except User.DoesNotExist:
                return Response({"error": "Неверные учетные данные"}, status=401)

            if not user.check_password(password):
                return Response({"error": "Неверные учетные данные"}, status=401)

            access_token, refresh_token = user.generate_tokens()
            return Response(
                {
                    "user": UserSerializer(user).data,
                    "tokens": {"access": access_token, "refresh": refresh_token},
                }
            )
        return Response(serializer.errors, status=400)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Выход выполнен успешно"})


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh токен обязателен"}, status=400)

        payload = User.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return Response({"error": "Неверный refresh токен"}, status=401)

        try:
            user = User.objects.get(id=payload["user_id"], is_active=True)
        except User.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=401)

        access_token, refresh_token = user.generate_tokens()
        return Response({"tokens": {"access": access_token, "refresh": refresh_token}})


class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UserUpdateSerializer
        return UserSerializer


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete(soft_delete=True)
        return Response({"message": "Аккаунт удален"}, status=204)
