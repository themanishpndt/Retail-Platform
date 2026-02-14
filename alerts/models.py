from django.db import models
from inventory.models import Store, InventoryLevel


class Alert(models.Model):
    """System alerts for various conditions."""
    ALERT_TYPES = [
        ('LOW_STOCK', 'Low Stock'),
        ('OVERSTOCK', 'Overstock'),
        ('STOCKOUT', 'Stockout'),
        ('ANOMALY', 'Anomaly Detected'),
        ('DEMAND_SPIKE', 'Demand Spike'),
        ('SLOW_MOVING', 'Slow Moving Item'),
        ('EXPIRATION', 'Expiration Warning'),
        ('DELIVERY_DELAY', 'Delivery Delay'),
        ('SYSTEM', 'System Alert'),
    ]

    SEVERITY_LEVELS = [
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('CRITICAL', 'Critical'),
        ('URGENT', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]

    alert_id = models.CharField(max_length=100, unique=True)
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='WARNING')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', db_index=True)
    
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='alerts')
    inventory_level = models.ForeignKey(InventoryLevel, on_delete=models.SET_NULL, null=True, blank=True)
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    recommended_action = models.TextField(blank=True)
    
    triggered_at = models.DateTimeField(auto_now_add=True, db_index=True)
    acknowledged_at = models.DateTimeField(blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['store', 'status']),
            models.Index(fields=['alert_type', 'severity']),
            models.Index(fields=['status', 'triggered_at']),
        ]

    def __str__(self):
        return f"{self.alert_type} - {self.title}"


class AlertNotification(models.Model):
    """Send notifications for alerts."""
    CHANNEL_CHOICES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification'),
        ('SLACK', 'Slack'),
        ('WEBHOOK', 'Webhook'),
    ]

    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='notifications')
    channel = models.CharField(max_length=50, choices=CHANNEL_CHOICES)
    recipient = models.CharField(max_length=255)  # Email, phone, user ID, etc.
    
    message = models.TextField()
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)
    
    response_status = models.CharField(max_length=50, blank=True)  # Success, Failed, Bounced, etc.
    response_details = models.JSONField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification: {self.alert.title} via {self.channel}"


class AlertRule(models.Model):
    """Configurable alert rules."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    alert_type = models.CharField(max_length=50, choices=Alert.ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=Alert.SEVERITY_LEVELS, default='WARNING')
    
    # Trigger conditions (JSON-based for flexibility)
    condition = models.JSONField()  # e.g., {"field": "quantity", "operator": "<", "value": 10}
    
    # Notification settings
    is_active = models.BooleanField(default=True)
    notify_channels = models.JSONField(default=list)  # ['EMAIL', 'PUSH', 'SLACK']
    notify_recipients = models.JSONField(default=list)  # Email addresses, user IDs, etc.
    
    # Throttling
    throttle_minutes = models.PositiveIntegerField(default=0, help_text="Minimum minutes between alerts")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['alert_type', 'name']

    def __str__(self):
        return self.name


class AlertHistory(models.Model):
    """Historical record of all alerts."""
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='history')
    
    status_before = models.CharField(max_length=20)
    status_after = models.CharField(max_length=20)
    changed_by = models.CharField(max_length=255, blank=True)
    change_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Alert {self.alert.alert_id} changed from {self.status_before} to {self.status_after}"
