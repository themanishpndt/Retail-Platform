from rest_framework import serializers
from inventory.models import Store, InventoryLevel, InventoryTransaction, StockMovement


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'store_id', 'name', 'location', 'manager', 'email', 'phone', 'is_active', 'created_at', 'updated_at']


class InventoryLevelSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    is_low_stock = serializers.SerializerMethodField()
    is_overstock = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryLevel
        fields = [
            'id', 'product', 'product_sku', 'store', 'store_name',
            'quantity_on_hand', 'quantity_reserved', 'quantity_available',
            'last_counted_at', 'last_restock_at', 'is_low_stock', 'is_overstock',
            'created_at', 'updated_at'
        ]
    
    def get_is_low_stock(self, obj):
        return obj.is_low_stock()
    
    def get_is_overstock(self, obj):
        return obj.is_overstock()


class InventoryTransactionSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source='inventory_level.product.sku', read_only=True)
    store_name = serializers.CharField(source='inventory_level.store.name', read_only=True)
    
    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'inventory_level', 'product_sku', 'store_name',
            'transaction_type', 'quantity_change', 'reference_doc',
            'notes', 'performed_by', 'created_at', 'updated_at'
        ]


class StockMovementSerializer(serializers.ModelSerializer):
    from_store_name = serializers.CharField(source='from_store.name', read_only=True)
    to_store_name = serializers.CharField(source='to_store.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'transfer_id', 'from_store', 'from_store_name',
            'to_store', 'to_store_name', 'product', 'product_sku',
            'quantity', 'reason', 'status', 'created_at',
            'shipped_at', 'received_at', 'updated_at'
        ]
