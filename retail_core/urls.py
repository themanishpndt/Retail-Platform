"""
URL Configuration for retail_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .dashboard_views import DashboardView
from .api_views import (
    DashboardAPIView, SalesAPIView, InventoryAPIView, 
    ForecastingAPIView, ShelfVisionAPIView, AlertsAPIView
)
from .smtp_api import TestSMTPView, SaveSMTPSettingsView
from .web_views import (
    ProductListView, ProductDetailView, ProductCreateView, ProductUpdateView, ProductDeleteView,
    InventoryListView, InventoryDetailView,
    OrderListView, OrderDetailView,
    AnalyticsDashboardView, ReportsView, StubView, SettingsView, DashboardTestView,
    ForecastingDashboardView, ShelfVisionDashboardView, AlertsDashboardView,
    # Sales Reports
    DailySalesReportView, MonthlySalesReportView, SalesByProductReportView, SalesByCategoryReportView,
    # Inventory Reports
    StockLevelsReportView, LowStockAlertReportView, StockMovementReportView, InventoryValuationReportView,
    # Customer Reports
    CustomerPurchasesReportView, TopCustomersReportView, CustomerRetentionReportView,
    # Performance Reports
    ProfitMarginReportView, SupplierPerformanceReportView, ForecastAccuracyReportView,
    # Export & Filter APIs
    ExportAllReportsView, ApplyFiltersView
)

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # Admin Custom Authentication
    path('admin/auth/', include('retail_core.auth_urls')),
    
    # Admin Panel (uncomment if admin_management app is available)
    # path('admin-panel/', include('admin.urls')),
    
    # User Authentication
    path('', include('retail_core.user_urls')),
    
    # Dashboard
    path('', DashboardView.as_view(), name='dashboard'),
    path('dashboard/', DashboardView.as_view(), name='dashboard-home'),
    
    # Dashboard API (for AJAX calls)
    path('api/dashboard/', DashboardAPIView.as_view(), name='api_dashboard'),
    path('api/sales/', SalesAPIView.as_view(), name='api_sales'),
    path('api/inventory/', InventoryAPIView.as_view(), name='api_inventory'),
    path('api/forecasting/', ForecastingAPIView.as_view(), name='api_forecasting'),
    path('api/shelf-vision/', ShelfVisionAPIView.as_view(), name='api_shelf_vision'),
    path('api/alerts/', AlertsAPIView.as_view(), name='api_alerts'),
    
    # Authentication (Web UI)
    path('accounts/', include('django.contrib.auth.urls')),

    
    # Products Web Interface
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/add/', ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    
    # Inventory Web Interface
    path('inventory/', InventoryListView.as_view(), name='inventory_list'),
    path('inventory/<int:pk>/', InventoryDetailView.as_view(), name='inventory_detail'),
    path('inventory/adjust/', InventoryAdjustView.as_view(), name='inventory_adjust'),
    path('inventory/transfer/', StubView.as_view(), name='stock_transfer'),
    
    # Orders Web Interface
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/create/', StubView.as_view(), name='order_create'),
    path('orders/<int:pk>/confirm/', StubView.as_view(), name='order_confirm'),
    
    # Analytics Web Interface
    path('analytics/', AnalyticsDashboardView.as_view(), name='analytics_dashboard'),
    path('reports/', ReportsView.as_view(), name='reports'),
    
    # Forecasting Web Interface
    path('forecasting/', ForecastingDashboardView.as_view(), name='forecasting'),
    
    # Shelf Vision Web Interface
    path('shelf-vision/', ShelfVisionDashboardView.as_view(), name='shelf_vision'),
    
    # Alerts Web Interface
    path('alerts/', AlertsDashboardView.as_view(), name='alerts'),
    
    # Settings
    path('settings/', SettingsView.as_view(), name='settings'),
    
    # Dashboard Test
    path('dashboard-test/', DashboardTestView.as_view(), name='dashboard_test'),
    
    # Stub routes
    path('stub/', StubView.as_view(), name='stub'),
    
    # Sales Reports
    path('reports/daily-sales/', DailySalesReportView.as_view(), name='report_daily_sales'),
    path('reports/monthly-sales/', MonthlySalesReportView.as_view(), name='report_monthly_sales'),
    path('reports/sales-by-product/', SalesByProductReportView.as_view(), name='report_sales_by_product'),
    path('reports/sales-by-category/', SalesByCategoryReportView.as_view(), name='report_sales_by_category'),
    
    # Inventory Reports
    path('reports/stock-levels/', StockLevelsReportView.as_view(), name='report_stock_levels'),
    path('reports/low-stock/', LowStockAlertReportView.as_view(), name='report_low_stock'),
    path('reports/stock-movement/', StockMovementReportView.as_view(), name='report_stock_movement'),
    path('reports/inventory-valuation/', InventoryValuationReportView.as_view(), name='report_inventory_valuation'),
    
    # Customer Reports
    path('reports/customer-purchases/', CustomerPurchasesReportView.as_view(), name='report_customer_purchases'),
    path('reports/top-customers/', TopCustomersReportView.as_view(), name='report_top_customers'),
    path('reports/customer-retention/', CustomerRetentionReportView.as_view(), name='report_customer_retention'),
    
    # Performance Reports
    path('reports/profit-margin/', ProfitMarginReportView.as_view(), name='report_profit_margin'),
    path('reports/supplier-performance/', SupplierPerformanceReportView.as_view(), name='report_supplier_performance'),
    path('reports/forecast-accuracy/', ForecastAccuracyReportView.as_view(), name='report_forecast_accuracy'),
    
    # Export & Filter APIs
    path('api/reports/export-all/', ExportAllReportsView.as_view(), name='export_all_reports'),
    path('api/reports/apply-filters/', ApplyFiltersView.as_view(), name='apply_filters'),
    
    # SMTP Configuration APIs
    path('api/test-smtp/', TestSMTPView.as_view(), name='test_smtp'),
    path('api/save-smtp-settings/', SaveSMTPSettingsView.as_view(), name='save_smtp_settings'),
    
    # Authentication (API)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API URLs
    path('api/v1/products/', include('products.urls')),
    path('api/v1/inventory/', include('inventory.urls')),
    path('api/v1/orders/', include('orders.urls')),
    path('api/v1/analytics/', include('analytics.urls')),
    path('api/v1/alerts/', include('alerts.urls')),
    path('api/v1/forecasting/', include('ml_services.urls')),
    path('api/v1/vision/', include('cv_services.urls')),
    path('api/v1/data-ingestion/', include('data_ingestion.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
