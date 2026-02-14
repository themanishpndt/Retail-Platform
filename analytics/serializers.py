from rest_framework import serializers
from .models import (
    DailySalesMetrics, ProductSalesAnalytics, DemandForecast,
    InventoryHealthReport, BusinessInsights, CategoryAnalytics
)


class DailySalesMetricsSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    
    class Meta:
        model = DailySalesMetrics
        fields = [
            'id', 'store', 'store_name', 'date', 'total_sales', 'total_items_sold',
            'total_transactions', 'average_transaction_value', 'top_products',
            'peak_hours', 'created_at', 'updated_at'
        ]


class ProductSalesAnalyticsSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = ProductSalesAnalytics
        fields = [
            'id', 'product', 'product_sku', 'product_name', 'period_start', 'period_end',
            'total_quantity_sold', 'total_revenue', 'average_selling_price', 'total_cost',
            'gross_profit', 'profit_margin_percent', 'return_quantity', 'return_rate',
            'created_at', 'updated_at'
        ]


class DemandForecastSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    
    class Meta:
        model = DemandForecast
        fields = [
            'id', 'product', 'product_sku', 'product_name', 'store', 'store_name',
            'forecast_date', 'forecast_quantity', 'confidence_interval_lower',
            'confidence_interval_upper', 'forecast_method', 'accuracy_score',
            'created_at', 'updated_at'
        ]


class InventoryHealthReportSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    
    class Meta:
        model = InventoryHealthReport
        fields = [
            'id', 'store', 'store_name', 'report_date', 'total_sku_count',
            'low_stock_count', 'out_of_stock_count', 'overstock_count',
            'total_inventory_value', 'inventory_turnover_rate', 'dead_stock_value',
            'created_at', 'updated_at'
        ]


class BusinessInsightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessInsights
        fields = [
            'id', 'insight_type', 'title', 'description', 'impact_level',
            'recommended_action', 'related_entities', 'metrics', 'is_acknowledged',
            'acknowledged_at', 'acknowledged_by', 'created_at', 'updated_at'
        ]


class CategoryAnalyticsSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = CategoryAnalytics
        fields = [
            'id', 'category', 'category_name', 'period_start', 'period_end',
            'total_revenue', 'total_quantity_sold', 'average_order_value',
            'unique_customers', 'return_rate', 'created_at', 'updated_at'
        ]
