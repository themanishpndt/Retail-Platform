"""
Analytics API Views
REST endpoints for business intelligence and reporting
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Avg, Count, F, Q
from datetime import datetime, timedelta

from .models import (
    DailySalesMetrics, ProductSalesAnalytics, DemandForecast,
    InventoryHealthReport, BusinessInsights, CategoryAnalytics
)
from .serializers import (
    DailySalesMetricsSerializer, ProductSalesAnalyticsSerializer,
    DemandForecastSerializer, InventoryHealthReportSerializer,
    BusinessInsightsSerializer, CategoryAnalyticsSerializer
)


class DailySalesMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for daily sales metrics"""
    
    queryset = DailySalesMetrics.objects.select_related('store')
    serializer_class = DailySalesMetricsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    # filterset_fields = ['store', 'date']
    ordering_fields = ['date', 'total_revenue']
    ordering = ['-date']
    
    def get_queryset(self):
        """Filter by date range"""
        queryset = super().get_queryset()
        
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        return queryset
        
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get sales summary for period"""
        queryset = self.get_queryset()
        
        summary = queryset.aggregate(
            total_revenue=Sum('total_revenue'),
            total_orders=Sum('order_count'),
            total_items=Sum('items_sold'),
            avg_order_value=Avg('average_order_value'),
            avg_daily_revenue=Avg('total_revenue')
        )
        
        return Response(summary)
        
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Get sales trends"""
        days = int(request.query_params.get('days', 30))
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        data = DailySalesMetrics.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).values('date').annotate(
            revenue=Sum('total_revenue'),
            orders=Sum('order_count')
        ).order_by('date')
        
        return Response(list(data))


class DemandForecastViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for demand forecasts"""
    
    queryset = DemandForecast.objects.select_related('product', 'store')
    serializer_class = DemandForecastSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    # filterset_fields = ['product', 'store', 'forecast_type']
    ordering_fields = ['forecast_date', 'predicted_demand']
    ordering = ['-forecast_date']
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming forecasts"""
        days = int(request.query_params.get('days', 7))
        end_date = datetime.now().date() + timedelta(days=days)
        
        forecasts = self.get_queryset().filter(
            forecast_date__gte=datetime.now().date(),
            forecast_date__lte=end_date
        )
        
        serializer = self.get_serializer(forecasts, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def high_demand(self, request):
        """Get products with high forecasted demand"""
        threshold = int(request.query_params.get('threshold', 100))
        
        forecasts = self.get_queryset().filter(
            forecast_date__gte=datetime.now().date(),
            predicted_demand__gte=threshold
        ).order_by('-predicted_demand')[:20]
        
        serializer = self.get_serializer(forecasts, many=True)
        return Response(serializer.data)


class InventoryHealthReportViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for inventory health reports"""
    
    queryset = InventoryHealthReport.objects.select_related('store')
    serializer_class = InventoryHealthReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    # filterset_fields = ['store', 'report_date']
    ordering_fields = ['report_date', 'health_score']
    ordering = ['-report_date']
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest health report"""
        store_id = request.query_params.get('store')
        
        if store_id:
            report = self.get_queryset().filter(store_id=store_id).first()
        else:
            report = self.get_queryset().first()
            
        if report:
            serializer = self.get_serializer(report)
            return Response(serializer.data)
        return Response({'message': 'No reports found'}, status=status.HTTP_404_NOT_FOUND)


class BusinessInsightsViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for AI-generated business insights"""
    
    queryset = BusinessInsights.objects.all()
    serializer_class = BusinessInsightsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    # filterset_fields = ['insight_type', 'priority', 'is_actionable']
    ordering_fields = ['generated_at', 'priority']
    ordering = ['-generated_at', '-priority']
    
    @action(detail=False, methods=['get'])
    def actionable(self, request):
        """Get actionable insights"""
        insights = self.get_queryset().filter(is_actionable=True)
        serializer = self.get_serializer(insights, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def high_priority(self, request):
        """Get high priority insights"""
        insights = self.get_queryset().filter(priority__gte=8)
        serializer = self.get_serializer(insights, many=True)
        return Response(serializer.data)


class AnalyticsDashboardView(viewsets.ViewSet):
    """Unified analytics dashboard endpoint"""
    
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get complete dashboard data"""
        today = datetime.now().date()
        thirty_days_ago = today - timedelta(days=30)
        
        # Sales metrics
        from orders.models import Order, OrderLine
        sales_stats = Order.objects.filter(
            order_date__gte=thirty_days_ago,
            status='completed'
        ).aggregate(
            total_revenue=Sum('total_amount'),
            total_orders=Count('id'),
            avg_order_value=Avg('total_amount')
        )
        
        # Inventory metrics
        from inventory.models import InventoryLevel
        inventory_stats = InventoryLevel.objects.aggregate(
            total_products=Count('product', distinct=True),
            total_stock=Sum('quantity_on_hand'),
            low_stock_count=Count('id', filter=Q(quantity_on_hand__lte=F('reorder_point'))),
            overstock_count=Count('id', filter=Q(quantity_on_hand__gt=F('max_stock_level')))
        )
        
        # Top products
        top_products = OrderLine.objects.filter(
            order__order_date__gte=thirty_days_ago,
            order__status='completed'
        ).values('product__name').annotate(
            quantity=Sum('quantity'),
            revenue=Sum('line_total')
        ).order_by('-revenue')[:10]
        
        # Recent insights
        insights = BusinessInsights.objects.filter(
            is_actionable=True
        ).order_by('-generated_at')[:5]
        
        dashboard = {
            'sales': sales_stats,
            'inventory': inventory_stats,
            'top_products': list(top_products),
            'insights': BusinessInsightsSerializer(insights, many=True).data,
            'period': {
                'start_date': thirty_days_ago.isoformat(),
                'end_date': today.isoformat()
            }
        }
        
        return Response(dashboard)
