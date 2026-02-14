from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, OrderViewSet, PurchaseOrderViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customers')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchase-orders')

urlpatterns = router.urls
