from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import StoreViewSet, InventoryLevelViewSet, InventoryTransactionViewSet, StockMovementViewSet

router = DefaultRouter()
router.register(r'stores', StoreViewSet, basename='stores')
router.register(r'levels', InventoryLevelViewSet, basename='inventory-levels')
router.register(r'transactions', InventoryTransactionViewSet, basename='inventory-transactions')
router.register(r'movements', StockMovementViewSet, basename='stock-movements')

urlpatterns = router.urls
