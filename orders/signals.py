"""
Django signals for orders app.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order, OrderLine


@receiver(post_save, sender=Order)
def update_inventory_on_order(sender, instance, created, **kwargs):
    """Update inventory when order is created."""
    if created:
        # TODO: Deduct from inventory when order is confirmed
        pass


@receiver(post_save, sender=Order)
def generate_order_analytics(sender, instance, **kwargs):
    """Generate analytics data for order."""
    if instance.status == 'DELIVERED':
        # TODO: Generate order analytics and insights
        pass
