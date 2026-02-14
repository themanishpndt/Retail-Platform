from django.db import models


class DataSource(models.Model):
    """Data source configuration for ingestion."""
    SOURCE_TYPES = [
        ('CSV', 'CSV File'),
        ('JSON', 'JSON File'),
        ('EXCEL', 'Excel File'),
        ('API', 'External API'),
        ('DATABASE', 'Database'),
        ('POS', 'POS System'),
        ('ERP', 'ERP System'),
    ]

    name = models.CharField(max_length=255, unique=True)
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES)
    description = models.TextField(blank=True)
    
    # Configuration
    connection_config = models.JSONField()  # API keys, DB credentials, file paths, etc.
    field_mapping = models.JSONField()  # Maps external fields to internal model fields
    
    is_active = models.BooleanField(default=True)
    auto_sync_enabled = models.BooleanField(default=False)
    sync_frequency_minutes = models.PositiveIntegerField(default=60, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.source_type})"


class DataIngestionJob(models.Model):
    """Track data ingestion jobs."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('PARTIAL', 'Partially Completed'),
    ]

    job_id = models.CharField(max_length=100, unique=True)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='ingestion_jobs')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    duration_seconds = models.PositiveIntegerField(blank=True, null=True)
    
    records_processed = models.PositiveIntegerField(default=0)
    records_inserted = models.PositiveIntegerField(default=0)
    records_updated = models.PositiveIntegerField(default=0)
    records_failed = models.PositiveIntegerField(default=0)
    
    error_log = models.TextField(blank=True)
    warning_log = models.TextField(blank=True)
    
    file_path = models.CharField(max_length=500, blank=True)  # If file-based ingestion
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"Job {self.job_id} - {self.status}"


class DataValidationRule(models.Model):
    """Validation rules for ingested data."""
    RULE_TYPES = [
        ('REQUIRED', 'Required Field'),
        ('UNIQUE', 'Unique Value'),
        ('RANGE', 'Value Range'),
        ('PATTERN', 'Pattern Match'),
        ('CUSTOM', 'Custom Logic'),
    ]

    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='validation_rules')
    
    field_name = models.CharField(max_length=255)
    rule_type = models.CharField(max_length=50, choices=RULE_TYPES)
    rule_definition = models.JSONField()  # Rule-specific config
    
    error_message = models.CharField(max_length=500)
    is_critical = models.BooleanField(default=True)  # Critical rules block import
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['field_name']

    def __str__(self):
        return f"{self.field_name} - {self.rule_type}"


class DataTransformationLog(models.Model):
    """Log of data transformations applied."""
    job = models.ForeignKey(DataIngestionJob, on_delete=models.CASCADE, related_name='transformation_logs')
    
    field_name = models.CharField(max_length=255)
    original_value = models.TextField()
    transformed_value = models.TextField()
    transformation_applied = models.CharField(max_length=255)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transform: {self.field_name}"


class ImportedDataAudit(models.Model):
    """Audit trail for all imported data."""
    job = models.ForeignKey(DataIngestionJob, on_delete=models.CASCADE, related_name='audit_trail')
    
    model_name = models.CharField(max_length=255)  # Product, Order, etc.
    record_id = models.CharField(max_length=255)
    action = models.CharField(max_length=50)  # CREATE, UPDATE, DELETE
    
    before_data = models.JSONField(blank=True, null=True)
    after_data = models.JSONField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.model_name} {self.record_id} - {self.action}"
