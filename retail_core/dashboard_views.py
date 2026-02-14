"""
Dashboard Views
Web interface for analytics visualization
"""

from django.views.generic import TemplateView
from django.db.models import Sum, Count, Avg, F
from django.utils import timezone
from datetime import timedelta
from products.models import Product
from inventory.models import InventoryLevel
from orders.models import Order


class DashboardView(TemplateView):
    """Main analytics dashboard"""
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Retail Analytics Dashboard'
        context['user'] = self.request.user
        
        # Date calculations
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        
        # Calculate KPIs
        # Total Revenue (30 days)
        revenue_data = Order.objects.filter(
            order_date__gte=thirty_days_ago,
            status__in=['CONFIRMED', 'SHIPPED', 'DELIVERED']
        ).aggregate(total=Sum('total'))
        context['total_revenue'] = revenue_data['total'] or 0
        
        # Total Orders (30 days)
        context['total_orders'] = Order.objects.filter(
            order_date__gte=thirty_days_ago
        ).count()
        
        # Low Stock Items
        context['low_stock_items'] = InventoryLevel.objects.filter(
            quantity_on_hand__lte=F('product__reorder_point')
        ).count()
        
        # Average Order Value
        if context['total_orders'] > 0:
            context['avg_order_value'] = context['total_revenue'] / context['total_orders']
        else:
            context['avg_order_value'] = 0
        
        return context
