from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ForecastModelViewSet, ForecastingResultViewSet, RecommendationViewSet

router = DefaultRouter()
router.register(r'models', ForecastModelViewSet, basename='forecast-models')
router.register(r'results', ForecastingResultViewSet, basename='forecasting-results')
router.register(r'recommendations', RecommendationViewSet, basename='recommendations')

urlpatterns = router.urls
