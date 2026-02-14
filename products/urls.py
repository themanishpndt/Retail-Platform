from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, SupplierViewSet, ProductImageViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'products', ProductViewSet, basename='products')
router.register(r'suppliers', SupplierViewSet, basename='suppliers')
router.register(r'images', ProductImageViewSet, basename='product-images')

urlpatterns = router.urls
