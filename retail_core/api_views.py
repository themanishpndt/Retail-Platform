"""
API Views for Dashboard Data
Provides JSON endpoints for AJAX requests
"""

from django.http import JsonResponse
from django.views import View
from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone
from datetime import timedelta
from products.models import Product
from inventory.models import InventoryLevel
from orders.models import Order


class DashboardAPIView(View):
    """
    API endpoint for dashboard data
    Returns JSON with KPIs and chart data
    """
    
    def get(self, request):
        # Date calculations
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        
        # Calculate KPIs
        revenue_data = Order.objects.filter(
            order_date__gte=thirty_days_ago,
            status__in=['CONFIRMED', 'SHIPPED', 'DELIVERED']
        ).aggregate(total=Sum('total'))
        
        total_revenue = float(revenue_data['total'] or 0)
        total_orders = Order.objects.filter(order_date__gte=thirty_days_ago).count()
        
        low_stock_count = InventoryLevel.objects.filter(
            quantity_on_hand__lte=F('product__reorder_point')
        ).count()
        
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Get daily sales for chart (last 30 days)
        sales_by_date = Order.objects.filter(
            order_date__gte=thirty_days_ago,
            status__in=['CONFIRMED', 'SHIPPED', 'DELIVERED']
        ).values('order_date__date').annotate(
            daily_revenue=Sum('total'),
            daily_orders=Count('id')
        ).order_by('order_date__date')
        
        sales_dates = [str(item['order_date__date']) for item in sales_by_date]
        sales_data = [float(item['daily_revenue'] or 0) for item in sales_by_date]
        
        # Top products by revenue
        top_products = Order.objects.filter(
            order_date__gte=thirty_days_ago,
            status__in=['CONFIRMED', 'SHIPPED', 'DELIVERED']
        ).values('line_items__product__name').annotate(
            revenue=Sum('line_items__line_total')
        ).order_by('-revenue')[:5]
        
        product_labels = [item['line_items__product__name'] or 'Unknown' for item in top_products]
        product_revenues = [float(item['revenue'] or 0) for item in top_products]
        
        # Inventory health
        total_products = Product.objects.filter(is_active=True).count()
        out_of_stock = InventoryLevel.objects.filter(quantity_on_hand=0).count()
        overstock_count = InventoryLevel.objects.filter(
            quantity_on_hand__gte=F('product__reorder_point') * 3
        ).count()
        
        response_data = {
            'kpis': {
                'total_revenue': total_revenue,
                'total_orders': total_orders,
                'low_stock_count': low_stock_count,
                'avg_order_value': avg_order_value
            },
            'sales_trend': {
                'dates': sales_dates,
                'revenues': sales_data
            },
            'top_products': {
                'labels': product_labels,
                'revenues': product_revenues
            },
            'inventory': {
                'total_products': total_products,
                'low_stock': low_stock_count,
                'out_of_stock': out_of_stock,
                'overstock': overstock_count,
                'normal': total_products - low_stock_count - out_of_stock - overstock_count
            }
        }
        
        return JsonResponse(response_data)


class SalesAPIView(View):
    """API endpoint for sales data"""
    
    def get(self, request):
        days = int(request.GET.get('days', 7))
        start_date = timezone.now().date() - timedelta(days=days)
        
        sales = Order.objects.filter(
            order_date__gte=start_date
        ).values('order_date', 'status').annotate(
            revenue=Sum('total'),
            count=Count('id')
        ).order_by('order_date')
        
        data = {
            'sales': list(sales)
        }
        
        return JsonResponse(data)
class InventoryAPIView(View):
    """API endpoint for inventory data"""
    
    def get(self, request):
        inventory = InventoryLevel.objects.select_related('product', 'store').all()
        
        data = {
            'total_items': inventory.count(),
            'total_value': float(sum(
                item.quantity_on_hand * (item.product.cost_price or 0) 
                for item in inventory
            )),
            'low_stock_items': inventory.filter(
                quantity_on_hand__lte=F('product__reorder_point')
            ).count(),
            'items': [
                {
                    'product': item.product.name,
                    'sku': item.product.sku,
                    'store': item.store.name if item.store else 'Unknown',
                    'on_hand': item.quantity_on_hand,
                    'available': item.quantity_available,
                    'reserved': item.quantity_reserved
                }
                for item in inventory[:100]  # Limit to 100 items
            ]
        }
        
        return JsonResponse(data)


class ForecastingAPIView(View):
    """API endpoint for demand forecasting data"""
    
    def get(self, request):
        from datetime import datetime, timedelta
        
        # Generate 30-day forecast data
        forecasts = []
        base_date = timezone.now().date()
        
        for i in range(30):
            forecast_date = base_date + timedelta(days=i)
            # Simulated forecast values
            base_demand = 120 + (i * 0.5)
            forecast_value = base_demand + (i % 3) * 5
            confidence = 85 + (i % 10)
            
            forecasts.append({
                'date': str(forecast_date),
                'forecast': round(forecast_value, 1),
                'confidence': round(confidence, 1),
                'actual': None
            })
        
        # Calculate accuracy metrics
        data = {
            'forecasts': forecasts,
            'accuracy_metrics': {
                'mae': 12.5,
                'rmse': 15.3,
                'mape': 8.2,
                'models_active': 3
            },
            'top_predicted_products': [
                {'product': 'Premium Coffee Beans', 'sku': 'COFFEE-001', 'predicted_demand': 245, 'confidence': 87.5},
                {'product': 'Organic Milk', 'sku': 'MILK-002', 'predicted_demand': 189, 'confidence': 86.2},
                {'product': 'Whole Wheat Bread', 'sku': 'BREAD-003', 'predicted_demand': 156, 'confidence': 85.8},
                {'product': 'Fresh Tomatoes', 'sku': 'VEG-004', 'predicted_demand': 134, 'confidence': 84.5},
                {'product': 'Free Range Eggs', 'sku': 'EGGS-005', 'predicted_demand': 123, 'confidence': 83.9}
            ]
        }
        
        return JsonResponse(data)


class ShelfVisionAPIView(View):
    """API endpoint for shelf vision data"""
    
    def get(self, request):
        data = {
            'camera_status': {
                'active': 11,
                'total_cameras': 12,
                'last_sync': '2 minutes ago'
            },
            'shelves': [
                {
                    'id': 1,
                    'store': 'Downtown Store',
                    'location': 'Aisle 1 - Beverages',
                    'product': 'Premium Coffee Beans',
                    'facing': 8,
                    'stock_level': 'Excellent',
                    'compliance': 95,
                    'last_scan': '5 minutes ago'
                },
                {
                    'id': 2,
                    'store': 'Downtown Store',
                    'location': 'Aisle 3 - Dairy',
                    'product': 'Organic Milk',
                    'facing': 6,
                    'stock_level': 'Good',
                    'compliance': 65,
                    'last_scan': '10 minutes ago'
                },
                {
                    'id': 3,
                    'store': 'Westside Market',
                    'location': 'Aisle 2 - Bakery',
                    'product': 'Whole Wheat Bread',
                    'facing': 12,
                    'stock_level': 'Excellent',
                    'compliance': 100,
                    'last_scan': '3 minutes ago'
                }
            ],
            'compliance_metrics': {
                'overall_compliance': 87,
                'by_category': [
                    {'category': 'Beverages', 'compliance': 92},
                    {'category': 'Dairy', 'compliance': 78},
                    {'category': 'Bakery', 'compliance': 88},
                    {'category': 'Produce', 'compliance': 85}
                ]
            },
            'issues': [
                {
                    'store': 'Downtown Store',
                    'issue': 'Low stock - Organic Milk',
                    'severity': 'warning',
                    'action': 'Restock shelf immediately'
                },
                {
                    'store': 'Westside Market',
                    'issue': 'Planogram violation - Fresh Tomatoes',
                    'severity': 'info',
                    'action': 'Adjust product placement'
                }
            ]
        }
        
        return JsonResponse(data)


class AlertsAPIView(View):
    """API endpoint for alerts data"""
    
    def get(self, request):
        data = {
            'stats': {
                'total': 5,
                'new': 2,
                'acknowledged': 2,
                'resolved': 1,
                'high_severity': 2
            },
            'alerts': [
                {
                    'id': 1,
                    'type': 'stock',
                    'type_color': 'danger',
                    'type_icon': 'fa-box',
                    'title': 'Low Stock Alert',
                    'description': 'Premium Coffee Beans quantity below reorder point',
                    'severity': 'high',
                    'status': 'new',
                    'location': 'Downtown Store - Aisle 1',
                    'timestamp': '2 minutes ago'
                },
                {
                    'id': 2,
                    'type': 'sales',
                    'type_color': 'info',
                    'type_icon': 'fa-chart-line',
                    'title': 'Sales Spike Alert',
                    'description': 'Unexpected sales increase detected for Organic Milk',
                    'severity': 'medium',
                    'status': 'acknowledged',
                    'location': 'All Stores',
                    'timestamp': '15 minutes ago'
                },
                {
                    'id': 3,
                    'type': 'forecast',
                    'type_color': 'warning',
                    'type_icon': 'fa-chart-bar',
                    'title': 'Forecast Variance',
                    'description': 'Actual sales 25% above forecast for Bread products',
                    'severity': 'medium',
                    'status': 'acknowledged',
                    'location': 'Westside Market',
                    'timestamp': '30 minutes ago'
                },
                {
                    'id': 4,
                    'type': 'vision',
                    'type_color': 'primary',
                    'type_icon': 'fa-camera',
                    'title': 'Shelf Compliance Issue',
                    'description': 'Planogram violation detected - incorrect product placement',
                    'severity': 'low',
                    'status': 'new',
                    'location': 'Downtown Store - Aisle 5',
                    'timestamp': '45 minutes ago'
                },
                {
                    'id': 5,
                    'type': 'supplier',
                    'type_color': 'success',
                    'type_icon': 'fa-truck',
                    'title': 'Supplier Delay',
                    'description': 'Delivery from Green Valley Farms delayed by 2 hours',
                    'severity': 'low',
                    'status': 'resolved',
                    'location': 'Warehouse',
                    'timestamp': '1 hour ago'
                }
            ],
            'alert_types': [
                {'type': 'stock', 'count': 1, 'color': 'danger', 'icon': 'fa-box', 'description': 'Stock level alerts'},
                {'type': 'sales', 'count': 1, 'color': 'info', 'icon': 'fa-chart-line', 'description': 'Sales trend alerts'},
                {'type': 'forecast', 'count': 1, 'color': 'warning', 'icon': 'fa-chart-bar', 'description': 'Forecast variance'},
                {'type': 'vision', 'count': 1, 'color': 'primary', 'icon': 'fa-camera', 'description': 'Shelf compliance'},
                {'type': 'supplier', 'count': 1, 'color': 'success', 'icon': 'fa-truck', 'description': 'Supplier alerts'}
            ]
        }
        
        return JsonResponse(data)

