"""
Orders API Views
REST endpoints for sales and purchase orders
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Avg, Q
from datetime import datetime, timedelta

from .models import Customer, Order, OrderLine, PurchaseOrder, POLine
from .serializers import (
    CustomerSerializer, OrderListSerializer, OrderDetailSerializer, OrderLineSerializer,
    PurchaseOrderSerializer, PurchaseOrderLineSerializer
)


class CustomerViewSet(viewsets.ModelViewSet):
    """API endpoint for customers"""
    
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email', 'phone', 'customer_code']
    ordering_fields = ['name', 'total_purchases', 'created_at']
    ordering = ['-total_purchases']
    
    @action(detail=True, methods=['get'])
    def purchase_history(self, request, pk=None):
        """Get customer purchase history"""
        customer = self.get_object()
        orders = Order.objects.filter(customer=customer).order_by('-order_date')[:20]
        serializer = OrderSerializer(orders, many=True, context={'request': request})
        return Response(serializer.data)
        
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get customer statistics"""
        customer = self.get_object()
        
        stats = Order.objects.filter(customer=customer, status='completed').aggregate(
            total_orders=Count('id'),
            total_spent=Sum('total_amount'),
            avg_order_value=Avg('total_amount'),
            total_items=Sum('orderline__quantity')
        )
        
        # Top products
        from django.db.models import Count
        top_products = OrderLine.objects.filter(
            order__customer=customer,
            order__status='completed'
        ).values('product__name').annotate(
            quantity=Sum('quantity')
        ).order_by('-quantity')[:5]
        
        stats['top_products'] = list(top_products)
        return Response(stats)


class OrderViewSet(viewsets.ModelViewSet):
    """API endpoint for sales orders"""
    
    queryset = Order.objects.select_related('customer', 'store').prefetch_related('line_items')
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    # filterset_fields = ['customer', 'store', 'status', 'payment_status']
    search_fields = ['order_number', 'customer__name', 'customer__email']
    ordering_fields = ['order_date', 'total_amount', 'created_at']
    ordering = ['-order_date']
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve and create/update"""
        if self.action in ['retrieve', 'create', 'update', 'partial_update']:
            return OrderDetailSerializer
        return OrderListSerializer
    
    def get_queryset(self):
        """Custom filtering"""
        queryset = super().get_queryset()
        
        # Date range filtering
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(order_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(order_date__lte=end_date)
            
        return queryset
        
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's orders"""
        today = datetime.now().date()
        orders = self.get_queryset().filter(order_date__date=today)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending orders"""
        orders = self.get_queryset().filter(status__in=['draft', 'confirmed'])
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
        
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm order"""
        order = self.get_object()
        
        if order.status != 'draft':
            return Response(
                {'error': 'Only draft orders can be confirmed'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        order.status = 'confirmed'
        order.save()
        
        # Update inventory
        from inventory.models import InventoryLevel, InventoryTransaction
        
        for line in order.lines.all():
            inventory, _ = InventoryLevel.objects.get_or_create(
                store=order.store,
                product=line.product
            )
            
            # Deduct stock
            inventory.quantity_on_hand -= line.quantity
            inventory.save()
            
            # Record transaction
            InventoryTransaction.objects.create(
                inventory_level=inventory,
                transaction_type='sale',
                quantity_change=-line.quantity,
                quantity_after=inventory.quantity_on_hand,
                reference_number=order.order_number
            )
            
        serializer = self.get_serializer(order)
        return Response(serializer.data)
        
    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        """Mark order as shipped"""
        order = self.get_object()
        
        if order.status not in ['confirmed', 'processing']:
            return Response(
                {'error': 'Order must be confirmed first'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        order.status = 'shipped'
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
        
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark order as completed"""
        order = self.get_object()
        order.status = 'completed'
        order.payment_status = 'paid'
        order.save()
        
        # Update customer total
        order.customer.total_purchases = Order.objects.filter(
            customer=order.customer,
            status='completed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        order.customer.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """API endpoint for purchase orders"""
    
    queryset = PurchaseOrder.objects.select_related('supplier', 'store').prefetch_related('line_items')
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    # filterset_fields = ['supplier', 'store', 'status']
    ordering_fields = ['order_date', 'expected_delivery', 'total_amount']
    ordering = ['-order_date']
    
    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        """Receive purchase order"""
        po = self.get_object()
        
        if po.status != 'confirmed':
            return Response(
                {'error': 'Only confirmed POs can be received'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Update inventory
        from inventory.models import InventoryLevel, InventoryTransaction
        
        for line in po.lines.all():
            inventory, _ = InventoryLevel.objects.get_or_create(
                store=po.store,
                product=line.product
            )
            
            # Add stock
            inventory.quantity_on_hand += line.quantity
            inventory.last_restocked = datetime.now()
            inventory.save()
            
            # Record transaction
            InventoryTransaction.objects.create(
                inventory_level=inventory,
                transaction_type='purchase',
                quantity_change=line.quantity,
                quantity_after=inventory.quantity_on_hand,
                reference_number=po.po_number
            )
            
        po.status = 'received'
        po.save()
        
        serializer = self.get_serializer(po)
        return Response(serializer.data)
