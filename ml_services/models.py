from django.db import models
from products.models import Product
from inventory.models import Store


class ForecastModel(models.Model):
    """ML model for demand forecasting."""
    MODEL_TYPES = [
        ('ARIMA', 'ARIMA'),
        ('LSTM', 'LSTM Neural Network'),
        ('PROPHET', 'Facebook Prophet'),
        ('ENSEMBLE', 'Ensemble Model'),
    ]

    name = models.CharField(max_length=255, unique=True)
    model_type = models.CharField(max_length=50, choices=MODEL_TYPES)
    description = models.TextField(blank=True)
    
    # Model configuration
    parameters = models.JSONField(default=dict)
    features_used = models.JSONField(default=list)  # List of feature names
    
    # Performance metrics
    mape = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # Mean Absolute Percentage Error
    rmse = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Root Mean Squared Error
    r_squared = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    training_data_points = models.PositiveIntegerField(default=0)
    training_accuracy = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    validation_accuracy = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    # Model lifecycle
    is_active = models.BooleanField(default=True)
    model_file_path = models.CharField(max_length=500, blank=True)  # Path to saved model
    
    last_trained_at = models.DateTimeField(blank=True, null=True)
    last_used_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ForecastingTrainingJob(models.Model):
    """Track forecasting model training jobs."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    model = models.ForeignKey(ForecastModel, on_delete=models.CASCADE, related_name='training_jobs')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    duration_seconds = models.PositiveIntegerField(blank=True, null=True)
    
    training_data_date_from = models.DateField()
    training_data_date_to = models.DateField()
    
    parameters_used = models.JSONField()
    error_message = models.TextField(blank=True)
    log_output = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"Training: {self.model.name} - {self.status}"


class DemandForecastingResult(models.Model):
    """Detailed demand forecasting results."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='forecast_results')
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    model = models.ForeignKey(ForecastModel, on_delete=models.SET_NULL, null=True, blank=True)
    
    forecast_date = models.DateField()
    forecast_period = models.CharField(max_length=50, default='DAILY')  # DAILY, WEEKLY, MONTHLY
    
    # Forecast values
    predicted_demand = models.DecimalField(max_digits=10, decimal_places=2)
    lower_bound = models.DecimalField(max_digits=10, decimal_places=2)  # Confidence interval
    upper_bound = models.DecimalField(max_digits=10, decimal_places=2)
    confidence_level = models.DecimalField(max_digits=3, decimal_places=2, default=0.95)  # 0-1
    
    # Actual data (filled later)
    actual_demand = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    forecast_accuracy = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'store', 'forecast_date', 'model')
        ordering = ['-forecast_date']

    def __str__(self):
        return f"Forecast: {self.product.sku} - {self.forecast_date}"


class ForecastingMetrics(models.Model):
    """Aggregate forecasting performance metrics."""
    model = models.OneToOneField(ForecastModel, on_delete=models.CASCADE, related_name='metrics')
    
    total_predictions = models.PositiveIntegerField(default=0)
    accurate_predictions = models.PositiveIntegerField(default=0)  # Count within ±10%
    
    overall_mape = models.DecimalField(max_digits=5, decimal_places=2)
    overall_rmse = models.DecimalField(max_digits=10, decimal_places=2)
    
    best_performing_category = models.CharField(max_length=255, blank=True)
    worst_performing_category = models.CharField(max_length=255, blank=True)
    
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Metrics: {self.model.name}"
