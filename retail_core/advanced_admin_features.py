"""
Advanced Admin Dashboard Backend Features
==========================================

This module extends the basic Django admin with advanced features:
- Custom admin actions with bulk operations
- Advanced filters and search
- Real-time statistics and reporting
- Activity logging and audit trails
- Custom dashboard widgets
- Performance optimizations
"""

from django.contrib import admin
from django.utils.html import format_html, mark_safe
from django.urls import reverse
from django.db.models import QuerySet, Count, Sum, Avg, Q
from django.utils import timezone
from django.shortcuts import render
from django.http import JsonResponse
from functools import wraps
import json
from datetime import datetime, timedelta


# ==================== ADMIN DECORATORS ====================

def admin_action(description=None):
    """Decorator for custom admin actions"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, queryset):
            return func(self, request, queryset)
        wrapper.short_description = description or func.__name__
        return wrapper
    return decorator


def require_permission(permission):
    """Decorator to check permissions for admin views"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            if not request.user.has_perm(permission):
                return admin.site.site_header_error(request)
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator


# ==================== ADVANCED FILTERS ====================

class AdvancedListFilter(admin.SimpleListFilter):
    """Base class for advanced filters with custom logic"""
    
    def queryset(self, request, queryset):
        """Override to implement advanced filtering"""
        if self.value():
            return queryset.filter(**{self.parameter_name: self.value()})
        return queryset


class DateRangeFilter(admin.SimpleListFilter):
    """Filter by date range"""
    title = 'Date Range'
    parameter_name = 'date_range'
    
    def lookups(self, request, model_admin):
        return [
            ('today', 'Today'),
            ('this_week', 'This Week'),
            ('this_month', 'This Month'),
            ('this_year', 'This Year'),
            ('last_7_days', 'Last 7 Days'),
            ('last_30_days', 'Last 30 Days'),
            ('last_90_days', 'Last 90 Days'),
        ]
    
    def queryset(self, request, queryset):
        now = timezone.now()
        filter_dict = {}
        
        if self.value() == 'today':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            filter_dict = {f'{self.parameter_name}__range': (start, end)}
        
        elif self.value() == 'this_week':
            start = now - timedelta(days=now.weekday())
            filter_dict = {f'{self.parameter_name}__gte': start}
        
        elif self.value() == 'this_month':
            start = now.replace(day=1, hour=0, minute=0, second=0)
            filter_dict = {f'{self.parameter_name}__gte': start}
        
        elif self.value() == 'this_year':
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0)
            filter_dict = {f'{self.parameter_name}__gte': start}
        
        elif self.value() == 'last_7_days':
            start = now - timedelta(days=7)
            filter_dict = {f'{self.parameter_name}__gte': start}
        
        elif self.value() == 'last_30_days':
            start = now - timedelta(days=30)
            filter_dict = {f'{self.parameter_name}__gte': start}
        
        elif self.value() == 'last_90_days':
            start = now - timedelta(days=90)
            filter_dict = {f'{self.parameter_name}__gte': start}
        
        if filter_dict:
            return queryset.filter(**filter_dict)
        return queryset


class StatusFilter(admin.SimpleListFilter):
    """Filter by active/inactive status"""
    title = 'Status'
    parameter_name = 'status'
    
    def lookups(self, request, model_admin):
        return [
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active=True)
        elif self.value() == 'inactive':
            return queryset.filter(is_active=False)
        return queryset


# ==================== ADVANCED ADMIN ACTIONS ====================

class AdvancedAdminMixin:
    """Mixin providing advanced admin functionality"""
    
    # Advanced configuration
    change_list_template = 'admin/advanced_change_list.html'
    change_form_template = 'admin/advanced_change_form.html'
    
    # Show custom stats on admin
    show_statistics = True
    statistics_fields = []
    
    # Enable bulk actions
    enable_bulk_actions = True
    bulk_actions_list = []
    
    # Enable activity logging
    enable_logging = True
    log_changes = True
    
    # Search enhancements
    enhanced_search = True
    search_help_text = None
    
    def get_readonly_fields(self, request, obj=None):
        """Add created/updated fields as read-only"""
        readonly = list(self.readonly_fields)
        if hasattr(self.model, 'created_at'):
            readonly.append('created_at')
        if hasattr(self.model, 'updated_at'):
            readonly.append('updated_at')
        return readonly
    
    def changelist_view(self, request, extra_context=None):
        """Enhanced changelist view with statistics"""
        extra_context = extra_context or {}
        
        if self.show_statistics:
            extra_context['statistics'] = self.get_statistics()
        
        if self.enable_bulk_actions:
            extra_context['bulk_actions'] = self.get_bulk_actions()
        
        extra_context['search_help'] = self.search_help_text
        extra_context['show_advanced_filters'] = True
        
        return super().changelist_view(request, extra_context)
    
    def get_statistics(self):
        """Calculate statistics for the model"""
        queryset = self.get_queryset(None)  # Initial queryset
        stats = {
            'total_count': queryset.count(),
        }
        
        # Add field-specific statistics
        for field in self.statistics_fields:
            if field == 'is_active':
                stats['active_count'] = queryset.filter(is_active=True).count()
                stats['inactive_count'] = queryset.filter(is_active=False).count()
            elif field == 'created_at':
                today = timezone.now().date()
                stats['created_today'] = queryset.filter(
                    created_at__date=today
                ).count()
        
        return stats
    
    def get_bulk_actions(self):
        """Get available bulk actions"""
        return [
            ('activate', 'Activate Selected'),
            ('deactivate', 'Deactivate Selected'),
            ('delete', 'Delete Selected'),
        ]
    
    def render_display_field(self, value, field_type='text'):
        """Render field values with proper formatting"""
        if isinstance(value, bool):
            color = '#28a745' if value else '#dc3545'
            text = 'Yes' if value else 'No'
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
                color, text
            )
        
        if isinstance(value, (int, float)):
            return format_html('<strong>{}</strong>', value)
        
        return value
    
    def get_search_help(self):
        """Get search help text"""
        return f"Search by: {', '.join(self.search_fields)}"
    
    def log_change(self, request, obj, message):
        """Log changes to the model"""
        if self.enable_logging:
            super().log_change(request, obj, message)
    
    def save_model(self, request, obj, form, change):
        """Save model and log changes"""
        super().save_model(request, obj, form, change)
        if self.log_changes:
            action = 'modified' if change else 'created'
            self.log_change(request, obj, f'Model {action} by {request.user}')
    
    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related"""
        queryset = super().get_queryset(request)
        
        # Add optimizations
        if hasattr(self, 'select_related_fields'):
            for field in self.select_related_fields:
                queryset = queryset.select_related(field)
        
        if hasattr(self, 'prefetch_related_fields'):
            for field in self.prefetch_related_fields:
                queryset = queryset.prefetch_related(field)
        
        return queryset


# ==================== ADMIN MIXIN FOR COMMON FIELDS ====================

class TimestampedAdminMixin:
    """Mixin for models with created_at and updated_at"""
    
    readonly_fields = ['created_at', 'updated_at', 'display_timestamps']
    
    def display_timestamps(self, obj):
        """Display creation and update times"""
        if not obj.pk:
            return "-"
        
        created = obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
        updated = obj.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        
        return format_html(
            '<div style="padding: 1rem; background: #f5f5f5; border-radius: 4px;">'
            '<strong>Created:</strong> {}<br>'
            '<strong>Updated:</strong> {}'
            '</div>',
            created, updated
        )
    
    display_timestamps.short_description = 'Timestamps'
    
    fieldsets = (
        ('Information', {
            'fields': ('display_timestamps',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Automatically managed timestamps'
        }),
    )


# ==================== DASHBOARD ADMIN ====================

class DashboardAdmin(AdvancedAdminMixin, admin.ModelAdmin):
    """Custom admin dashboard with statistics and analytics"""
    
    change_list_template = 'admin/custom_dashboard.html'
    
    def changelist_view(self, request, extra_context=None):
        """Custom dashboard view"""
        extra_context = extra_context or {}
        
        # Add dashboard statistics
        extra_context['dashboard_stats'] = self.get_dashboard_statistics()
        extra_context['recent_items'] = self.get_recent_items()
        extra_context['alerts'] = self.get_alerts()
        extra_context['charts'] = self.get_chart_data()
        
        return super().changelist_view(request, extra_context)
    
    def get_dashboard_statistics(self):
        """Calculate dashboard-wide statistics"""
        from products.models import Product
        from orders.models import Order
        from analytics.models import DailySalesMetrics
        
        stats = {
            'total_products': Product.objects.count(),
            'total_orders': Order.objects.count(),
            'total_sales': DailySalesMetrics.objects.aggregate(
                Sum('total_sales')
            )['total_sales__sum'] or 0,
            'pending_orders': Order.objects.filter(status='pending').count(),
        }
        
        return stats
    
    def get_recent_items(self):
        """Get recently created items"""
        return {
            'products': self.model.objects.all().order_by('-created_at')[:5],
            'orders': self.model.objects.all().order_by('-created_at')[:5],
        }
    
    def get_alerts(self):
        """Get system alerts"""
        alerts = []
        
        from inventory.models import InventoryLevel
        low_stock = InventoryLevel.objects.filter(quantity__lt=100)
        if low_stock.exists():
            alerts.append({
                'type': 'warning',
                'message': f'{low_stock.count()} items have low stock',
                'count': low_stock.count(),
            })
        
        return alerts
    
    def get_chart_data(self):
        """Get data for dashboard charts"""
        from analytics.models import DailySalesMetrics
        from django.db.models import Sum
        from datetime import timedelta
        
        today = timezone.now().date()
        last_7_days = today - timedelta(days=7)
        
        sales_data = DailySalesMetrics.objects.filter(
            date__gte=last_7_days
        ).values('date').annotate(
            total=Sum('total_sales')
        ).order_by('date')
        
        return {
            'labels': [str(item['date']) for item in sales_data],
            'values': [item['total'] for item in sales_data],
        }


# ==================== API VIEWS FOR DASHBOARD ====================

def get_dashboard_data(request):
    """API endpoint for dashboard real-time data"""
    data = {
        'status': 'operational',
        'timestamp': timezone.now().isoformat(),
        'statistics': {},
        'alerts': [],
        'performance': {},
    }
    
    return JsonResponse(data)


def get_quick_stats(request):
    """API endpoint for quick statistics"""
    from products.models import Product
    from orders.models import Order
    
    stats = {
        'products': Product.objects.count(),
        'orders': Order.objects.count(),
        'active_users': 0,  # Implement based on your auth system
        'api_calls': 0,  # Implement based on your API tracking
    }
    
    return JsonResponse(stats)


# ==================== EXPORT FUNCTIONALITY ====================

import csv
from django.http import HttpResponse


def export_as_csv(modeladmin, request, queryset):
    """Generic CSV export action"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{modeladmin.model._meta.verbose_name_plural}.csv"'
    
    writer = csv.writer(response)
    
    # Write headers
    headers = [field.name for field in modeladmin.model._meta.fields]
    writer.writerow(headers)
    
    # Write data
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in headers])
    
    return response

export_as_csv.short_description = "Export selected items as CSV"


# ==================== UTILITY FUNCTIONS ====================

def format_number(value, prefix='', suffix=''):
    """Format numbers for display"""
    if value is None:
        return '-'
    
    if isinstance(value, (int, float)):
        if value >= 1_000_000:
            return f'{prefix}{value/1_000_000:.1f}M{suffix}'
        elif value >= 1_000:
            return f'{prefix}{value/1_000:.1f}K{suffix}'
    
    return f'{prefix}{value}{suffix}'


def get_trend_indicator(current, previous):
    """Get visual trend indicator"""
    if previous == 0:
        trend = 0
    else:
        trend = ((current - previous) / previous) * 100
    
    if trend > 0:
        color = '#28a745'
        arrow = '↑'
    elif trend < 0:
        color = '#dc3545'
        arrow = '↓'
    else:
        color = '#6c757d'
        arrow = '→'
    
    return format_html(
        '<span style="color: {};">{} {:.1f}%</span>',
        color, arrow, abs(trend)
    )


def get_status_badge(status):
    """Get visual status badge"""
    badges = {
        'active': '#28a745',
        'inactive': '#6c757d',
        'pending': '#ffc107',
        'completed': '#17a2b8',
        'failed': '#dc3545',
        'processing': '#007bff',
    }
    
    color = badges.get(status, '#6c757d')
    
    return format_html(
        '<span style="background-color: {}; color: white; padding: 3px 10px; '
        'border-radius: 3px; font-weight: 600; text-transform: uppercase; '
        'font-size: 0.85rem;">{}</span>',
        color, status
    )


# ==================== ADMIN CONFIGURATION ====================

# Customize admin site
admin.site.site_header = 'Retail Platform Administration'
admin.site.site_title = 'Retail Admin'
admin.site.index_title = 'Welcome to Retail Platform Administration'

# Add custom CSS and JavaScript
admin.site.extrastyle = mark_safe('''
    <link rel="stylesheet" href="/static/admin/css/advanced_admin.css">
''')

admin.site.extrahead = mark_safe('''
    <script src="/static/admin/js/advanced_admin.js"></script>
    <style>
        #header { background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%); }
        .sidebar { background: #f5f7fa; }
        .stat-card { border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    </style>
''')
