"""
Django signals for products app.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from products.models import Product


@receiver(pre_save, sender=Product)
def calculate_product_margin(sender, instance, **kwargs):
    """Calculate margin percentage before saving product."""
    instance.calculate_margin()


@receiver(post_save, sender=Product)
def create_product_search_index(sender, instance, created, **kwargs):
    """Create search index for new products."""
    if created:
        # TODO: Index product in search engine (Elasticsearch, etc.)
        pass
