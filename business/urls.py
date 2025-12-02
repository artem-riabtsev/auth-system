from django.urls import path

from .views import OrdersView, ProductsView, StoresView

urlpatterns = [
    path("products/", ProductsView.as_view(), name="products"),
    path("orders/", OrdersView.as_view(), name="orders"),
    path("stores/", StoresView.as_view(), name="stores"),
    # path('users/demo/', UserManagementDemoView.as_view(), name='users-demo'),
]
