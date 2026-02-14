from rest_framework import serializers
from orders.models import Customer, Order, OrderLine, PurchaseOrder, POLine


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'customer_id', 'name', 'email', 'phone', 'address',
                  'city', 'loyalty_points', 'is_active', 'created_at', 'updated_at']


class OrderLineSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    
    class Meta:
        model = OrderLine
        fields = ['id', 'order', 'product', 'product_sku', 'product_name',
                  'quantity', 'unit_price', 'line_total', 'discount_percent', 'notes']


class OrderListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_id', 'customer_name', 'store_name', 'order_date',
                  'status', 'total', 'payment_method', 'created_at']


class OrderDetailSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    line_items = OrderLineSerializer(many=True, read_only=True)
    customer_id = serializers.IntegerField(write_only=True)
    store_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'customer', 'customer_id', 'store', 'store_id',
            'order_date', 'status', 'subtotal', 'tax', 'discount', 'total',
            'payment_method', 'notes', 'line_items', 'created_at', 'updated_at',
            'shipped_at', 'delivered_at'
        ]


class PurchaseOrderLineSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = POLine
        fields = ['id', 'purchase_order', 'product', 'product_sku', 'product_name',
                  'quantity_ordered', 'quantity_received', 'unit_cost']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    line_items = PurchaseOrderLineSerializer(many=True, read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'po_number', 'supplier', 'supplier_name', 'store', 'store_name',
            'order_date', 'expected_delivery', 'status', 'subtotal', 'tax', 'total',
            'notes', 'line_items', 'created_at', 'updated_at'
        ]
