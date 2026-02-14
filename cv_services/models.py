from django.db import models
from products.models import Product, ProductImage
from inventory.models import Store


class StockLevelDetectionTask(models.Model):
    """Computer vision task for real-time stock level detection."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    task_id = models.CharField(max_length=100, unique=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='cv_tasks')
    image = models.ImageField(upload_to='cv_tasks/%Y/%m/%d/')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    processing_start_time = models.DateTimeField(blank=True, null=True)
    processing_end_time = models.DateTimeField(blank=True, null=True)
    
    detected_items = models.JSONField(default=dict)  # {product_id: quantity}
    confidence_scores = models.JSONField(default=dict)  # {product_id: confidence}
    
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"CV Task {self.task_id} - {self.status}"


class ProductDetectionModel(models.Model):
    """YOLO or other CV model for product detection."""
    name = models.CharField(max_length=255, unique=True)
    model_type = models.CharField(max_length=100, default='YOLO8')  # YOLO8, Faster R-CNN, etc.
    description = models.TextField(blank=True)
    
    # Model configuration
    model_file_path = models.CharField(max_length=500)
    confidence_threshold = models.DecimalField(max_digits=3, decimal_places=2, default=0.5)
    
    # Performance metrics
    mAP = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # Mean Average Precision
    inference_time_ms = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    trained_on_categories = models.JSONField(default=list)
    
    last_trained_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ShelfAnalysisResult(models.Model):
    """Shelf analysis using computer vision."""
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='shelf_analysis')
    shelf_location = models.CharField(max_length=255)  # Aisle, Shelf ID, etc.
    image = models.ImageField(upload_to='shelf_analysis/%Y/%m/%d/')
    
    analysis_date = models.DateTimeField(auto_now_add=True)
    
    # Analysis results
    total_facings = models.PositiveIntegerField()  # Total product placements visible
    products_detected = models.JSONField(default=dict)  # {product_id: count}
    missing_products = models.JSONField(default=list)  # Products expected but not found
    out_of_stock_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    shelf_quality_score = models.DecimalField(max_digits=3, decimal_places=2)  # 0-1
    is_compliant_with_display_policy = models.BooleanField()
    
    ai_model_used = models.ForeignKey(ProductDetectionModel, on_delete=models.SET_NULL, null=True, blank=True)
    confidence_average = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    recommendations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-analysis_date']

    def __str__(self):
        return f"Shelf Analysis: {self.store.name} - {self.shelf_location}"


class ProductRecognitionData(models.Model):
    """Training data for product recognition."""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='cv_training_data')
    
    # Visual characteristics
    color = models.CharField(max_length=100, blank=True)
    size_category = models.CharField(max_length=50, blank=True)  # Small, Medium, Large
    packaging_material = models.CharField(max_length=100, blank=True)
    
    # Reference images
    reference_images = models.JSONField(default=list)  # Paths or IDs of reference images
    
    # Recognition features (extracted from images)
    dominant_colors = models.JSONField(default=list)
    texture_features = models.JSONField(default=dict)
    shape_descriptor = models.CharField(max_length=255, blank=True)
    
    is_trained = models.BooleanField(default=False)
    trained_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CV Data: {self.product.sku}"


class VisionAnalyticMetrics(models.Model):
    """Aggregate metrics for computer vision analysis."""
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='vision_metrics')
    metric_date = models.DateField()
    
    total_images_processed = models.PositiveIntegerField(default=0)
    detection_accuracy = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    average_processing_time = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    stock_visibility_accuracy = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    shelf_compliance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    detected_anomalies = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('store', 'metric_date')
        ordering = ['-metric_date']

    def __str__(self):
        return f"Vision Metrics: {self.store.name} - {self.metric_date}"
