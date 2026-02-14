"""
Django signals for inventory app.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from inventory.models import InventoryTransaction, InventoryLevel


@receiver(post_save, sender=InventoryTransaction)
def update_inventory_level(sender, instance, created, **kwargs):
    """Update inventory level after transaction is created."""
    if created:
        inv_level = instance.inventory_level
        inv_level.update_available_quantity()


@receiver(post_save, sender=InventoryLevel)
def check_inventory_alerts(sender, instance, created, **kwargs):
    """Check inventory alerts after level update."""
    if instance.is_low_stock():
        # TODO: Trigger low stock alert
        pass
    elif instance.is_overstock():
        # TODO: Trigger overstock alert
        pass
