from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DailySalesMetricsViewSet, DemandForecastViewSet,
    InventoryHealthReportViewSet, BusinessInsightsViewSet,
    AnalyticsDashboardView
)

router = DefaultRouter()
router.register(r'daily-sales-metrics', DailySalesMetricsViewSet, basename='daily-sales-metrics')
router.register(r'forecasts', DemandForecastViewSet, basename='demand-forecasts')
router.register(r'inventory-health', InventoryHealthReportViewSet, basename='inventory-health')
router.register(r'insights', BusinessInsightsViewSet, basename='business-insights')
router.register(r'dashboard', AnalyticsDashboardView, basename='analytics-dashboard')

urlpatterns = router.urls
