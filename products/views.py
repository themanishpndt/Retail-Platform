"""
Products API Views
REST endpoints for product management
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Avg

from .models import Category, Product, Supplier, ProductImage
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    SupplierSerializer, ProductImageSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """API endpoint for product categories"""
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    # filterset_fields = ['parent', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get all products in this category"""
        category = self.get_object()
        products = Product.objects.filter(category=category, is_active=True)
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get category hierarchy tree"""
        root_categories = Category.objects.filter(parent=None, is_active=True)
        
        def build_tree(category):
            return {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'product_count': category.product_set.filter(is_active=True).count(),
                'children': [build_tree(child) for child in category.subcategories.filter(is_active=True)]
            }
            
        tree = [build_tree(cat) for cat in root_categories]
        return Response(tree)


class ProductViewSet(viewsets.ModelViewSet):
    """API endpoint for products"""
    
    queryset = Product.objects.select_related('category', 'supplier').prefetch_related('images')
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    # filterset_fields = ['category', 'supplier', 'is_active']
    search_fields = ['name', 'sku', 'description', 'barcode']
    ordering_fields = ['name', 'cost_price', 'selling_price', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve and create/update"""
        if self.action in ['retrieve', 'create', 'update', 'partial_update']:
            return ProductDetailSerializer
        return ProductListSerializer
    
    def get_queryset(self):
        """Custom queryset filtering"""
        queryset = super().get_queryset()
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(selling_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(selling_price__lte=max_price)
            
        # Filter by low margin
        low_margin = self.request.query_params.get('low_margin')
        if low_margin:
            queryset = queryset.filter(profit_margin__lt=10)
            
        return queryset
        
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products below reorder point"""
        from inventory.models import InventoryLevel
        
        low_stock_items = InventoryLevel.objects.filter(
            quantity_on_hand__lte=F('reorder_point')
        ).select_related('product')
        
        products = [item.product for item in low_stock_items]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
        
    @action(detail=True, methods=['get'])
    def sales_stats(self, request, pk=None):
        """Get sales statistics for product"""
        from orders.models import OrderLine
        from django.db.models import Sum, Avg, Count
        from datetime import datetime, timedelta
        
        product = self.get_object()
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        stats = OrderLine.objects.filter(
            product=product,
            order__order_date__gte=thirty_days_ago,
            order__status='completed'
        ).aggregate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('line_total'),
            avg_quantity=Avg('quantity'),
            order_count=Count('order', distinct=True)
        )
        
        return Response(stats)
        
    @action(detail=True, methods=['post'])
    def update_price(self, request, pk=None):
        """Update product price"""
        product = self.get_object()
        new_price = request.data.get('selling_price')
        
        if not new_price:
            return Response({'error': 'selling_price required'}, status=status.HTTP_400_BAD_REQUEST)
            
        product.selling_price = new_price
        product.save()
        
        serializer = self.get_serializer(product)
        return Response(serializer.data)


class SupplierViewSet(viewsets.ModelViewSet):
    """API endpoint for suppliers"""
    
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email', 'phone', 'city']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get all products from this supplier"""
        supplier = self.get_object()
        products = Product.objects.filter(supplier=supplier, is_active=True)
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
        
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Get supplier performance metrics"""
        from orders.models import PurchaseOrder
        from django.db.models import Avg, Count
        
        supplier = self.get_object()
        
        metrics = PurchaseOrder.objects.filter(supplier=supplier).aggregate(
            total_orders=Count('id'),
            avg_lead_time=Avg('actual_delivery_days'),
            on_time_delivery_rate=Avg(
                Case(
                    When(actual_delivery_days__lte=F('expected_delivery_days'), then=100),
                    default=0,
                    output_field=FloatField()
                )
            )
        )
        
        return Response(metrics)


class ProductImageViewSet(viewsets.ModelViewSet):
    """API endpoint for product images"""
    
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = []
    # filterset_fields = ['product', 'is_primary']
