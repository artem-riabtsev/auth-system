from django.urls import path
from .views import CheckPermissionView, TestPermissionView

urlpatterns = [
    path('check-permissions/', CheckPermissionView.as_view(), name='check-permissions'),
    path('test-permission/', TestPermissionView.as_view(), name='test-permission'),
]