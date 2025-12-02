from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from permissions.utils import PermissionChecker

# Mock данные для демонстрации
MOCK_PRODUCTS = [
    {
        "id": 1,
        "name": "MacBook Pro",
        "price": 1999,
        "category": "Ноутбуки",
        "owner_id": 1,
    },
    {
        "id": 2,
        "name": "iPhone 15",
        "price": 999,
        "category": "Смартфоны",
        "owner_id": 2,
    },
    {"id": 3, "name": "iPad Air", "price": 599, "category": "Планшеты", "owner_id": 1},
    {
        "id": 4,
        "name": "Samsung TV",
        "price": 1299,
        "category": "Телевизоры",
        "owner_id": 3,
    },
]

MOCK_ORDERS = [
    {
        "id": 1,
        "product_id": 1,
        "quantity": 1,
        "total": 1999,
        "status": "completed",
        "owner_id": 1,
    },
    {
        "id": 2,
        "product_id": 2,
        "quantity": 2,
        "total": 1998,
        "status": "processing",
        "owner_id": 2,
    },
    {
        "id": 3,
        "product_id": 3,
        "quantity": 1,
        "total": 599,
        "status": "pending",
        "owner_id": 1,
    },
]

MOCK_STORES = [
    {"id": 1, "name": "Главный магазин", "location": "Москва", "employees": 15},
    {"id": 2, "name": "Филиал №1", "location": "Санкт-Петербург", "employees": 8},
    {"id": 3, "name": "Онлайн-склад", "location": "Казань", "employees": 5},
]


class ProductsView(APIView):
    """Демонстрация работы прав доступа к товарам"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Получить список товаров (фильтруется по правам)"""
        user_id = request.user.id

        # ПРОСТАЯ проверка прав
        has_permission = PermissionChecker.has_permission(
            user=request.user, element_code="products", permission_code="read"
        )

        if not has_permission:
            return Response(
                {"detail": "Нет прав для просмотра товаров"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Определяем scope прав пользователя
        user_perms = PermissionChecker.get_user_permissions(request.user)
        products_scope = user_perms.get("products", {}).get("read", "NONE")

        # Фильтруем товары по scope
        if products_scope == "ALL":
            visible_products = MOCK_PRODUCTS
        elif products_scope == "OWN":
            visible_products = [p for p in MOCK_PRODUCTS if p["owner_id"] == user_id]
        else:
            visible_products = []

        return Response(
            {
                "products": visible_products,
                "total": len(visible_products),
                "user_id": user_id,
                "scope": products_scope,
                "message": f"Видите товары в зависимости от прав: {products_scope}",
            }
        )


class OrdersView(APIView):
    """Демонстрация работы прав доступа к заказам"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Получить список заказов (фильтруется по правам)"""
        user_id = request.user.id

        has_permission = PermissionChecker.has_permission(
            user=request.user, element_code="orders", permission_code="read"
        )

        if not has_permission:
            return Response(
                {"detail": "Нет прав для просмотра заказов"},
                status=status.HTTP_403_FORBIDDEN,
            )

        user_perms = PermissionChecker.get_user_permissions(request.user)
        orders_scope = user_perms.get("orders", {}).get("read", "NONE")

        if orders_scope == "ALL":
            visible_orders = MOCK_ORDERS
        elif orders_scope == "OWN":
            visible_orders = [o for o in MOCK_ORDERS if o["owner_id"] == user_id]
        else:
            visible_orders = []

        return Response(
            {
                "orders": visible_orders,
                "total": len(visible_orders),
                "scope": orders_scope,
            }
        )


class StoresView(APIView):
    """Демонстрация работы прав доступа к магазинам"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Получить список магазинов"""
        has_permission = PermissionChecker.has_permission(
            user=request.user, element_code="stores", permission_code="read"
        )

        if not has_permission:
            return Response(
                {"detail": "Нет прав для просмотра магазинов"},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(
            {
                "stores": MOCK_STORES,
                "total": len(MOCK_STORES),
                "note": "Магазины видны всем кто имеет право read на stores",
            }
        )
