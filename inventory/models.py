from django.db import models
from django.core.validators import MinValueValidator
from products.models import Product


class Store(models.Model):
    """Store/Location model."""
    store_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    manager = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.store_id} - {self.name}"


class InventoryLevel(models.Model):
    """Real-time inventory levels per store."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_levels')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='inventory_levels')
    quantity_on_hand = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    quantity_reserved = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    quantity_available = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    
    last_counted_at = models.DateTimeField(blank=True, null=True)
    last_restock_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'store')
        ordering = ['product', 'store']
        indexes = [
            models.Index(fields=['product', 'store']),
            models.Index(fields=['quantity_on_hand']),
        ]

    def __str__(self):
        return f"{self.product.sku} @ {self.store.name}: {self.quantity_on_hand}"

    def update_available_quantity(self):
        """Calculate available quantity."""
        self.quantity_available = self.quantity_on_hand - self.quantity_reserved
        self.save(update_fields=['quantity_available'])

    def is_low_stock(self):
        """Check if inventory is below reorder point."""
        return self.quantity_available <= self.product.reorder_point

    def is_overstock(self):
        """Check if inventory exceeds max stock."""
        return self.quantity_on_hand > self.product.max_stock


class InventoryTransaction(models.Model):
    """Audit trail for all inventory movements."""
    TRANSACTION_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJUST', 'Adjustment'),
        ('TRANSFER', 'Transfer'),
        ('COUNT', 'Physical Count'),
        ('RETURN', 'Return'),
        ('DAMAGE', 'Damage/Loss'),
    ]

    inventory_level = models.ForeignKey(InventoryLevel, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity_change = models.IntegerField()  # Can be negative
    
    reference_doc = models.CharField(max_length=100, blank=True, help_text="PO, Invoice, Transfer ID, etc.")
    notes = models.TextField(blank=True)
    performed_by = models.CharField(max_length=255)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['inventory_level', 'created_at']),
            models.Index(fields=['transaction_type', 'created_at']),
        ]

    def __str__(self):
        return f"{self.transaction_type}: {self.quantity_change} @ {self.created_at}"

    def save(self, *args, **kwargs):
        """Update inventory level when transaction is created."""
        if not self.pk:  # New transaction
            old_quantity = self.inventory_level.quantity_on_hand
            self.inventory_level.quantity_on_hand += self.quantity_change
            self.inventory_level.save(update_fields=['quantity_on_hand'])
        super().save(*args, **kwargs)


class StockMovement(models.Model):
    """Track stock movements between stores."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_TRANSIT', 'In Transit'),
        ('RECEIVED', 'Received'),
        ('CANCELLED', 'Cancelled'),
    ]

    transfer_id = models.CharField(max_length=100, unique=True)
    from_store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='stock_sent')
    to_store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='stock_received')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transfers')
    
    quantity = models.PositiveIntegerField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    created_at = models.DateTimeField(auto_now_add=True)
    shipped_at = models.DateTimeField(blank=True, null=True)
    received_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['from_store', 'to_store']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"Transfer {self.transfer_id}: {self.quantity} x {self.product.sku}"
