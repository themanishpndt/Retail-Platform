from django.db import models
from inventory.models import Store
from products.models import Product


class DailySalesMetrics(models.Model):
    """Daily sales aggregated metrics."""
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='daily_metrics')
    date = models.DateField(db_index=True)
    
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_items_sold = models.PositiveIntegerField(default=0)
    total_transactions = models.PositiveIntegerField(default=0)
    average_transaction_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    top_products = models.JSONField(default=list, blank=True)
    peak_hours = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('store', 'date')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['store', 'date']),
        ]

    def __str__(self):
        return f"{self.store.name} - {self.date}"


class ProductSalesAnalytics(models.Model):
    """Product-level sales analytics."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales_analytics')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='product_analytics')
    date = models.DateField(db_index=True)
    
    quantity_sold = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    customer_reviews = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'store', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.product.sku} @ {self.store.name} - {self.date}"


class CategoryAnalytics(models.Model):
    """Category-level analytics."""
    category = models.ForeignKey('products.Category', on_delete=models.CASCADE, related_name='analytics')
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_quantity = models.PositiveIntegerField(default=0)
    avg_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('category', 'store', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.category.name} @ {self.store.name} - {self.date}"


class DemandForecast(models.Model):
    """ML-based demand forecasts."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='forecasts')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='forecasts')
    forecast_date = models.DateField(db_index=True)
    
    forecasted_demand = models.DecimalField(max_digits=10, decimal_places=2)
    confidence_level = models.DecimalField(max_digits=3, decimal_places=2, default=0.85)  # 0-1
    model_used = models.CharField(max_length=100, default='ARIMA')
    
    actual_demand = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    accuracy = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'store', 'forecast_date')
        ordering = ['-forecast_date']
        indexes = [
            models.Index(fields=['product', 'store', 'forecast_date']),
        ]

    def __str__(self):
        return f"Forecast: {self.product.sku} @ {self.store.name} - {self.forecast_date}"


class InventoryHealthReport(models.Model):
    """Inventory health metrics."""
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='inventory_health')
    report_date = models.DateField(auto_now_add=True, db_index=True)
    
    total_items_stocked = models.PositiveIntegerField(default=0)
    low_stock_items = models.PositiveIntegerField(default=0)
    overstock_items = models.PositiveIntegerField(default=0)
    dead_stock_items = models.PositiveIntegerField(default=0)
    
    total_inventory_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    inventory_turnover_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    storage_utilization = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage
    forecast_accuracy = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-report_date']

    def __str__(self):
        return f"Inventory Health: {self.store.name} - {self.report_date}"


class BusinessInsights(models.Model):
    """AI-generated business insights and recommendations."""
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='insights')
    insight_date = models.DateField(auto_now_add=True, db_index=True)
    
    INSIGHT_TYPES = [
        ('DEMAND', 'Demand Trend'),
        ('INVENTORY', 'Inventory Issue'),
        ('PRICING', 'Pricing Opportunity'),
        ('SALES', 'Sales Pattern'),
        ('ANOMALY', 'Anomaly Detection'),
        ('RECOMMENDATION', 'Recommendation'),
    ]
    
    insight_type = models.CharField(max_length=50, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    recommendation = models.TextField(blank=True)
    
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.8)
    impact_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.5)
    
    is_actioned = models.BooleanField(default=False)
    action_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-insight_date']

    def __str__(self):
        return f"{self.insight_type}: {self.title}"
