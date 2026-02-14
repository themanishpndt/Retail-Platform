from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import QuerySet
from products.models import Category, Supplier, Product, ProductImage
from inventory.models import Store, InventoryLevel, InventoryTransaction, StockMovement
from orders.models import Customer, Order, OrderLine, PurchaseOrder, POLine
from analytics.models import DailySalesMetrics, ProductSalesAnalytics, DemandForecast, BusinessInsights
from alerts.models import Alert, AlertNotification, AlertRule
from ml_services.models import ForecastModel, ForecastingTrainingJob
from cv_services.models import ProductDetectionModel, ShelfAnalysisResult
from data_ingestion.models import DataSource, DataIngestionJob


# ==================== CUSTOM ADMIN CLASSES ====================

class RetailAdminBase(admin.ModelAdmin):
    """Base admin class with common configurations"""
    date_hierarchy = None
    list_per_page = 50
    show_full_result_count = True
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = f'{self.opts.verbose_name_plural} Management'
        return super().changelist_view(request, extra_context)


class ReadOnlyTabularInline(admin.TabularInline):
    """Read-only inline for display purposes"""
    can_delete = False
    extra = 0
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False



# ==================== PRODUCT ADMINISTRATION ====================

@admin.register(Category)
class CategoryAdmin(RetailAdminBase):
    list_display = ['name', 'product_count', 'created_at']
    search_fields = ['name']
    ordering = ['-created_at']
    
    def product_count(self, obj):
        count = obj.products.count()
        return format_html(
            '<span style="background-color: #e7f3ff; padding: 3px 8px; border-radius: 3px;">{}</span>',
            count
        )
    product_count.short_description = 'Products'


@admin.register(Supplier)
class SupplierAdmin(RetailAdminBase):
    list_display = ['name', 'email', 'phone', 'status_badge', 'created_at']
    search_fields = ['name', 'email', 'phone']
    list_filter = ['is_active', 'created_at']
    fieldsets = (
        ('Basic Information', {'fields': ('name', 'email', 'phone', 'is_active')}),
        ('Address', {'fields': ('address', 'city', 'state', 'postal_code', 'country')}),
        ('Contact', {'fields': ('contact_person', 'contact_phone')}),
    )
    ordering = ['-created_at']
    
    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">Active</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">Inactive</span>'
        )
    status_badge.short_description = 'Status'


@admin.register(Product)
class ProductAdmin(RetailAdminBase):
    list_display = ['sku', 'name', 'category', 'price_display', 'status_badge', 'created_at']
    search_fields = ['sku', 'name', 'barcode']
    list_filter = ['category', 'is_active', 'is_discontinued', 'created_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('sku', 'barcode', 'name', 'description', 'category', 'supplier'),
            'description': 'Core product information'
        }),
        ('Pricing', {
            'fields': ('cost_price', 'selling_price', 'margin_percentage'),
            'classes': ('wide',)
        }),
        ('Stock Management', {
            'fields': ('reorder_point', 'reorder_quantity', 'max_stock'),
            'classes': ('collapse',)
        }),
        ('Physical Details', {
            'fields': ('unit_of_measure', 'weight', 'dimensions'),
            'classes': ('collapse',)
        }),
        ('Status', {'fields': ('is_active', 'is_discontinued')}),
    )
    readonly_fields = ['margin_percentage']
    ordering = ['-created_at']
    list_per_page = 30
    
    def price_display(self, obj):
        return format_html(
            '<span style="color: #28a745; font-weight: bold;">${:.2f}</span>',
            obj.selling_price or 0
        )
    price_display.short_description = 'Selling Price'
    
    def status_badge(self, obj):
        if obj.is_discontinued:
            return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 3px 10px; border-radius: 3px;">Discontinued</span>'
            )
        elif obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">Active</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">Inactive</span>'
        )
    status_badge.short_description = 'Status'


@admin.register(ProductImage)
class ProductImageAdmin(RetailAdminBase):
    list_display = ['product', 'image_preview', 'is_primary', 'uploaded_at']
    list_filter = ['product', 'is_primary', 'uploaded_at']
    ordering = ['-uploaded_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 3px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'




# ==================== INVENTORY ADMINISTRATION ====================

@admin.register(Store)
class StoreAdmin(RetailAdminBase):
    list_display = ['store_id', 'name', 'location', 'status_badge', 'created_at']
    search_fields = ['name', 'store_id', 'location']
    list_filter = ['is_active', 'created_at']
    fieldsets = (
        ('Store Information', {'fields': ('store_id', 'name', 'location', 'is_active')}),
        ('Contact', {'fields': ('phone', 'email')}),
        ('Manager', {'fields': ('manager_name',), 'classes': ('collapse',)}),
    )
    ordering = ['-created_at']
    
    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">✓ Active</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">✗ Inactive</span>'
        )
    status_badge.short_description = 'Status'


@admin.register(InventoryLevel)
class InventoryLevelAdmin(RetailAdminBase):
    list_display = ['product', 'store', 'quantity_display', 'availability_status', 'updated_at']
    search_fields = ['product__sku', 'store__name']
    list_filter = ['store', 'product__category', 'updated_at']
    ordering = ['product__name', 'store__name']
    list_per_page = 50
    
    def quantity_display(self, obj):
        color = 'green' if obj.quantity_available > 0 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.quantity_available
        )
    quantity_display.short_description = 'Available'
    
    def availability_status(self, obj):
        if obj.quantity_available == 0:
            return format_html('<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px;">Out of Stock</span>')
        elif obj.quantity_available <= obj.quantity_on_hand * 0.2:
            return format_html('<span style="background-color: #ffc107; color: black; padding: 3px 8px; border-radius: 3px;">Low Stock</span>')
        return format_html('<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">In Stock</span>')
    availability_status.short_description = 'Status'


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(RetailAdminBase):
    list_display = ['inventory_level', 'transaction_type', 'quantity_change', 'reference_doc', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['reference_doc', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    list_per_page = 50
    
    def has_delete_permission(self, request):
        # Prevent deletion of transactions for audit purposes
        return False


@admin.register(StockMovement)
class StockMovementAdmin(RetailAdminBase):
    list_display = ['transfer_id', 'from_store', 'to_store', 'quantity', 'status_badge', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['transfer_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'in_transit': '#17a2b8',
            'received': '#28a745',
            'cancelled': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'




# ==================== ORDERS ADMINISTRATION ====================

@admin.register(Customer)
class CustomerAdmin(RetailAdminBase):
    list_display = ['customer_id', 'name', 'email', 'loyalty_points_display', 'status_badge', 'created_at']
    search_fields = ['name', 'email', 'customer_id']
    list_filter = ['is_active', 'created_at']
    fieldsets = (
        ('Personal Information', {'fields': ('customer_id', 'name', 'email', 'phone')}),
        ('Address', {'fields': ('address', 'city', 'state', 'postal_code', 'country')}),
        ('Loyalty', {'fields': ('loyalty_points', 'membership_tier')}),
        ('Status', {'fields': ('is_active',)}),
    )
    ordering = ['-created_at']
    
    def loyalty_points_display(self, obj):
        return format_html(
            '<span style="background-color: #ffc107; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{} pts</span>',
            obj.loyalty_points
        )
    loyalty_points_display.short_description = 'Loyalty Points'
    
    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">Active</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">Inactive</span>'
        )
    status_badge.short_description = 'Status'


@admin.register(Order)
class OrderAdmin(RetailAdminBase):
    list_display = ['order_id', 'customer', 'store', 'total_display', 'status_badge', 'order_date']
    search_fields = ['order_id', 'customer__name']
    list_filter = ['status', 'order_date', 'store']
    readonly_fields = ['created_at', 'updated_at', 'total']
    ordering = ['-order_date']
    list_per_page = 30
    fieldsets = (
        ('Order Information', {'fields': ('order_id', 'customer', 'store', 'order_date')}),
        ('Financial', {'fields': ('total', 'notes')}),
        ('Status', {'fields': ('status',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    def total_display(self, obj):
        return format_html(
            '<span style="color: #28a745; font-weight: bold;">${:.2f}</span>',
            obj.total
        )
    total_display.short_description = 'Total'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'confirmed': '#17a2b8',
            'shipped': '#0069d9',
            'delivered': '#28a745',
            'cancelled': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(OrderLine)
class OrderLineAdmin(RetailAdminBase):
    list_display = ['order', 'product', 'quantity', 'unit_price', 'line_total_display']
    list_filter = ['order__store', 'order__order_date']
    ordering = ['-order__order_date']
    
    def line_total_display(self, obj):
        total = obj.quantity * obj.unit_price
        return format_html(
            '<span style="color: #28a745; font-weight: bold;">${:.2f}</span>',
            total
        )
    line_total_display.short_description = 'Line Total'


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(RetailAdminBase):
    list_display = ['po_number', 'supplier', 'store', 'total_display', 'status_badge', 'order_date']
    list_filter = ['status', 'order_date']
    search_fields = ['po_number', 'supplier__name']
    ordering = ['-order_date']
    
    def total_display(self, obj):
        return format_html(
            '<span style="color: #0069d9; font-weight: bold;">${:.2f}</span>',
            obj.total
        )
    total_display.short_description = 'Total'
    
    def status_badge(self, obj):
        colors = {
            'draft': '#6c757d',
            'pending': '#ffc107',
            'confirmed': '#17a2b8',
            'received': '#28a745',
            'cancelled': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'




# ==================== ANALYTICS ADMINISTRATION ====================

@admin.register(DailySalesMetrics)
class DailySalesMetricsAdmin(RetailAdminBase):
    list_display = ['store', 'date', 'sales_display', 'transactions_display']
    list_filter = ['store', 'date']
    ordering = ['-date']
    readonly_fields = ['total_sales', 'total_transactions', 'created_at']
    
    def sales_display(self, obj):
        return format_html(
            '<span style="color: #28a745; font-weight: bold;">${:.2f}</span>',
            obj.total_sales
        )
    sales_display.short_description = 'Total Sales'
    
    def transactions_display(self, obj):
        return format_html(
            '<span style="background-color: #e7f3ff; padding: 3px 8px; border-radius: 3px;">{}</span>',
            obj.total_transactions
        )
    transactions_display.short_description = 'Transactions'


@admin.register(DemandForecast)
class DemandForecastAdmin(RetailAdminBase):
    list_display = ['product', 'store', 'forecast_date', 'demand_display', 'confidence_display']
    list_filter = ['forecast_date', 'store']
    search_fields = ['product__sku']
    ordering = ['-forecast_date']
    
    def demand_display(self, obj):
        return format_html(
            '<span style="font-weight: bold;">{}</span>',
            obj.forecasted_demand
        )
    demand_display.short_description = 'Forecast'
    
    def confidence_display(self, obj):
        color = 'green' if obj.confidence_level > 0.8 else 'orange' if obj.confidence_level > 0.6 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1%}</span>',
            color,
            obj.confidence_level
        )
    confidence_display.short_description = 'Confidence'


@admin.register(BusinessInsights)
class BusinessInsightsAdmin(RetailAdminBase):
    list_display = ['title', 'insight_type', 'store', 'confidence_display', 'action_badge', 'insight_date']
    list_filter = ['insight_type', 'is_actioned', 'insight_date']
    search_fields = ['title', 'description']
    ordering = ['-insight_date']
    readonly_fields = ['insight_date']
    
    def confidence_display(self, obj):
        color = 'green' if obj.confidence_score > 0.8 else 'orange'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1%}</span>',
            color,
            obj.confidence_score
        )
    confidence_display.short_description = 'Confidence'
    
    def action_badge(self, obj):
        if obj.is_actioned:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">✓ Actioned</span>'
            )
        return format_html(
            '<span style="background-color: #ffc107; color: black; padding: 3px 8px; border-radius: 3px;">Pending</span>'
        )
    action_badge.short_description = 'Action'




# ==================== ALERTS ADMINISTRATION ====================

@admin.register(Alert)
class AlertAdmin(RetailAdminBase):
    list_display = ['alert_id', 'alert_type', 'severity_badge', 'status_badge', 'store', 'triggered_at']
    list_filter = ['alert_type', 'severity', 'status', 'triggered_at']
    search_fields = ['alert_id', 'title', 'description']
    readonly_fields = ['triggered_at', 'acknowledged_at', 'resolved_at']
    ordering = ['-triggered_at']
    list_per_page = 50
    fieldsets = (
        ('Alert Information', {'fields': ('alert_id', 'alert_type', 'title', 'description')}),
        ('Status', {'fields': ('severity', 'status')}),
        ('Store', {'fields': ('store',)}),
        ('Timestamps', {'fields': ('triggered_at', 'acknowledged_at', 'resolved_at')}),
    )
    
    def severity_badge(self, obj):
        colors = {
            'critical': '#dc3545',
            'high': '#fd7e14',
            'medium': '#ffc107',
            'low': '#17a2b8',
        }
        color = colors.get(obj.severity, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_severity_display()
        )
    severity_badge.short_description = 'Severity'
    
    def status_badge(self, obj):
        colors = {
            'open': '#dc3545',
            'acknowledged': '#ffc107',
            'resolved': '#28a745',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(AlertRule)
class AlertRuleAdmin(RetailAdminBase):
    list_display = ['name', 'alert_type', 'severity', 'status_badge', 'created_at']
    list_filter = ['alert_type', 'is_active', 'created_at']
    search_fields = ['name']
    ordering = ['-created_at']
    
    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">✓ Active</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 10px; border-radius: 3px;">Inactive</span>'
        )
    status_badge.short_description = 'Status'




# ==================== ML & CV SERVICES ADMINISTRATION ====================

@admin.register(ForecastModel)
class ForecastModelAdmin(RetailAdminBase):
    list_display = ['name', 'model_type', 'status_badge', 'mape_display', 'last_trained_at']
    list_filter = ['model_type', 'is_active', 'last_trained_at']
    search_fields = ['name']
    ordering = ['-last_trained_at']
    readonly_fields = ['mape', 'last_trained_at', 'created_at']
    
    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">✓ Active</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 10px; border-radius: 3px;">Inactive</span>'
        )
    status_badge.short_description = 'Status'
    
    def mape_display(self, obj):
        if obj.mape:
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.2f}%</span>',
                'green' if obj.mape < 10 else 'orange',
                obj.mape
            )
        return "—"
    mape_display.short_description = 'MAPE'


@admin.register(ForecastingTrainingJob)
class ForecastingTrainingJobAdmin(RetailAdminBase):
    list_display = ['model', 'status_badge', 'duration_display', 'start_time']
    list_filter = ['status', 'start_time']
    ordering = ['-start_time']
    readonly_fields = ['start_time', 'end_time', 'created_at']
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'running': '#17a2b8',
            'completed': '#28a745',
            'failed': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def duration_display(self, obj):
        if obj.end_time and obj.start_time:
            duration = obj.end_time - obj.start_time
            return f"{duration.total_seconds():.0f}s"
        return "—"
    duration_display.short_description = 'Duration'


@admin.register(ProductDetectionModel)
class ProductDetectionModelAdmin(RetailAdminBase):
    list_display = ['name', 'model_type', 'status_badge', 'mAP_display', 'created_at']
    list_filter = ['is_active', 'model_type', 'created_at']
    ordering = ['-created_at']
    
    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">✓ Active</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 10px; border-radius: 3px;">Inactive</span>'
        )
    status_badge.short_description = 'Status'
    
    def mAP_display(self, obj):
        if obj.mAP:
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.2f}%</span>',
                'green' if obj.mAP > 0.85 else 'orange',
                obj.mAP * 100
            )
        return "—"
    mAP_display.short_description = 'mAP'


@admin.register(ShelfAnalysisResult)
class ShelfAnalysisResultAdmin(RetailAdminBase):
    list_display = ['store', 'shelf_location', 'quality_display', 'analysis_date']
    list_filter = ['store', 'analysis_date']
    search_fields = ['shelf_location']
    ordering = ['-analysis_date']
    
    def quality_display(self, obj):
        score = obj.shelf_quality_score
        color = 'green' if score > 0.85 else 'orange' if score > 0.7 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1%}</span>',
            color,
            score
        )
    quality_display.short_description = 'Quality'




# ==================== DATA INGESTION ADMINISTRATION ====================

@admin.register(DataSource)
class DataSourceAdmin(RetailAdminBase):
    list_display = ['name', 'source_type', 'status_badge', 'sync_display', 'created_at']
    list_filter = ['source_type', 'is_active', 'created_at']
    search_fields = ['name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">✓ Active</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">Inactive</span>'
        )
    status_badge.short_description = 'Status'
    
    def sync_display(self, obj):
        if obj.auto_sync_enabled:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">Auto Sync</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 8px; border-radius: 3px;">Manual</span>'
        )
    sync_display.short_description = 'Sync Mode'


@admin.register(DataIngestionJob)
class DataIngestionJobAdmin(RetailAdminBase):
    list_display = ['job_id', 'data_source', 'status_badge', 'records_display', 'start_time']
    list_filter = ['status', 'start_time']
    search_fields = ['job_id']
    readonly_fields = ['start_time', 'end_time', 'created_at']
    ordering = ['-start_time']
    list_per_page = 50
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'running': '#17a2b8',
            'completed': '#28a745',
            'failed': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def records_display(self, obj):
        return format_html(
            '<span style="background-color: #e7f3ff; padding: 3px 8px; border-radius: 3px;">{} records</span>',
            obj.records_processed
        )
    records_display.short_description = 'Processed'




# ==================== ADMIN SITE CUSTOMIZATION ====================

class RetailAdminSite(admin.AdminSite):
    """Custom Admin Site for Retail Platform"""
    site_header = "Retail Analytics Platform"
    site_title = "Admin Portal"
    index_title = "Dashboard"
    
    def each_context(self, request):
        context = super().each_context(request)
        context.update({
            'site_header': self.site_header,
            'site_title': self.site_title,
        })
        return context


# Apply custom admin site (optional - uncomment to use)
# admin.site = RetailAdminSite(name='retail_admin')

# Standard admin site customization
admin.site.site_header = "🏪 Retail Analytics Platform"
admin.site.site_title = "Retail Admin Portal"
admin.site.index_title = "Welcome to Retail Platform Administration"

