"""Utility functions for the retail platform."""

from decimal import Decimal
from django.db.models import Q
from datetime import datetime, timedelta


def calculate_inventory_turnover(store_id, days=30):
    """
    Calculate inventory turnover ratio for a store.
    
    Formula: COGS / Average Inventory
    """
    from inventory.models import InventoryLevel
    from orders.models import Order, OrderLine
    
    try:
        # Get COGS (Cost of Goods Sold)
        cogs = OrderLine.objects.filter(
            order__store_id=store_id,
            order__order_date__gte=datetime.now() - timedelta(days=days)
        ).aggregate(
            total_cost=Sum('quantity' * F('product__cost_price'))
        )['total_cost'] or 0
        
        # Get average inventory value
        avg_inventory = InventoryLevel.objects.filter(
            store_id=store_id
        ).aggregate(
            avg_value=Avg(F('quantity_on_hand') * F('product__cost_price'))
        )['avg_value'] or 1
        
        if avg_inventory == 0:
            return 0
        
        return float(cogs) / float(avg_inventory)
    
    except Exception as e:
        print(f"Error calculating turnover: {e}")
        return 0


def get_low_stock_products(store_id):
    """Get all low-stock products in a store."""
    from inventory.models import InventoryLevel
    
    return InventoryLevel.objects.filter(
        store_id=store_id,
        quantity_available__lte=F('product__reorder_point')
    ).select_related('product', 'store')


def get_overstock_products(store_id):
    """Get all overstocked products in a store."""
    from inventory.models import InventoryLevel
    
    return InventoryLevel.objects.filter(
        store_id=store_id,
        quantity_on_hand__gt=F('product__max_stock')
    ).select_related('product', 'store')


def get_dead_stock_products(store_id, days=90):
    """Get products with no sales in specified days."""
    from inventory.models import InventoryLevel
    from orders.models import OrderLine
    
    # Get products with sales in the period
    products_with_sales = OrderLine.objects.filter(
        order__store_id=store_id,
        order__order_date__gte=datetime.now() - timedelta(days=days)
    ).values_list('product_id', flat=True).distinct()
    
    # Return products without sales
    return InventoryLevel.objects.filter(
        store_id=store_id,
        quantity_on_hand__gt=0
    ).exclude(
        product_id__in=products_with_sales
    ).select_related('product', 'store')


def format_currency(amount):
    """Format amount as currency."""
    return f"${amount:,.2f}"


def get_date_range(start_date, end_date):
    """Generate list of dates between start and end."""
    current = start_date
    dates = []
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)
    return dates


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
