"""
Inventory API Views
REST endpoints for inventory management
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F, Sum
from datetime import datetime, timedelta

from .models import Store, InventoryLevel, InventoryTransaction, StockMovement
from .serializers import (
    StoreSerializer, InventoryLevelSerializer,
    InventoryTransactionSerializer, StockMovementSerializer
)


class StoreViewSet(viewsets.ModelViewSet):
    """API endpoint for stores"""
    
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'city', 'address']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def inventory_summary(self, request, pk=None):
        """Get inventory summary for store"""
        store = self.get_object()
        
        summary = InventoryLevel.objects.filter(store=store).aggregate(
            total_products=Count('product', distinct=True),
            total_quantity=Sum('quantity_on_hand'),
            low_stock_count=Count('id', filter=Q(quantity_on_hand__lte=F('reorder_point'))),
            overstock_count=Count('id', filter=Q(quantity_on_hand__gt=F('max_stock_level')))
        )
        
        return Response(summary)


class InventoryLevelViewSet(viewsets.ModelViewSet):
    """API endpoint for inventory levels"""
    
    queryset = InventoryLevel.objects.select_related('product', 'store')
    serializer_class = InventoryLevelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    # filterset_fields = ['store', 'product']
    search_fields = ['product__name', 'product__sku', 'store__name']
    ordering_fields = ['quantity_on_hand', 'last_restocked', 'updated_at']
    ordering = ['-updated_at']
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get items below reorder point"""
        items = self.get_queryset().filter(quantity_on_hand__lte=F('reorder_point'))
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def overstock(self, request):
        """Get overstocked items"""
        items = self.get_queryset().filter(quantity_on_hand__gt=F('max_stock_level'))
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
        
    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """Manually adjust stock level"""
        inventory = self.get_object()
        quantity = request.data.get('quantity')
        reason = request.data.get('reason', 'Manual adjustment')
        
        if quantity is None:
            return Response({'error': 'quantity required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Create transaction
        InventoryTransaction.objects.create(
            inventory_level=inventory,
            transaction_type='adjustment',
            quantity_change=quantity,
            quantity_after=inventory.quantity_on_hand + quantity,
            notes=reason
        )
        
        inventory.quantity_on_hand += quantity
        inventory.save()
        
        serializer = self.get_serializer(inventory)
        return Response(serializer.data)


class InventoryTransactionViewSet(viewsets.ModelViewSet):
    """API endpoint for inventory transactions"""
    
    queryset = InventoryTransaction.objects.select_related('inventory_level', 'inventory_level__product')
    serializer_class = InventoryTransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    # filterset_fields = ['inventory_level', 'transaction_type']
    ordering_fields = ['transaction_date']
    ordering = ['-transaction_date']
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent transactions"""
        days = int(request.query_params.get('days', 7))
        since = datetime.now() - timedelta(days=days)
        
        transactions = self.get_queryset().filter(transaction_date__gte=since)
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)


class StockMovementViewSet(viewsets.ModelViewSet):
    """API endpoint for stock movements between stores"""
    
    queryset = StockMovement.objects.select_related('product', 'from_store', 'to_store')
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    # filterset_fields = ['from_store', 'to_store', 'product', 'status']
    ordering_fields = ['movement_date', 'created_at']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve stock transfer"""
        movement = self.get_object()
        
        if movement.status != 'pending':
            return Response(
                {'error': 'Only pending movements can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Update inventory levels
        from_inventory = InventoryLevel.objects.get(store=movement.from_store, product=movement.product)
        to_inventory, _ = InventoryLevel.objects.get_or_create(
            store=movement.to_store,
            product=movement.product,
            defaults={'quantity_on_hand': 0}
        )
        
        if from_inventory.quantity_on_hand < movement.quantity:
            return Response(
                {'error': 'Insufficient stock in source store'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Deduct from source
        from_inventory.quantity_on_hand -= movement.quantity
        from_inventory.save()
        
        # Add to destination
        to_inventory.quantity_on_hand += movement.quantity
        to_inventory.save()
        
        # Update movement status
        movement.status = 'completed'
        movement.save()
        
        serializer = self.get_serializer(movement)
        return Response(serializer.data)
