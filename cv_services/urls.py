from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProductDetectionModelViewSet, StockLevelDetectionTaskViewSet, ShelfAnalysisResultViewSet, ProductRecognitionViewSet

router = DefaultRouter()
router.register(r'detection-models', ProductDetectionModelViewSet, basename='detection-models')
router.register(r'detection-tasks', StockLevelDetectionTaskViewSet, basename='detection-tasks')
router.register(r'shelf-analysis', ShelfAnalysisResultViewSet, basename='shelf-analysis')
router.register(r'recognition', ProductRecognitionViewSet, basename='product-recognition')

urlpatterns = router.urls
