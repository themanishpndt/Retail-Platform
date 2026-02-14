from rest_framework import serializers
from products.models import Category, Supplier, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_person', 'email', 'phone', 'address', 
                  'city', 'country', 'payment_terms', 'is_active', 'created_at', 'updated_at']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'description', 'is_primary', 'uploaded_at']


class ProductListSerializer(serializers.ModelSerializer):
    """Simplified serializer for product lists."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'sku', 'name', 'category_name', 'supplier_name', 
                  'selling_price', 'cost_price', 'is_active', 'created_at']


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed product serializer with related objects."""
    category = CategorySerializer(read_only=True)
    supplier = SupplierSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    
    category_id = serializers.IntegerField(write_only=True)
    supplier_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'barcode', 'name', 'description', 'category', 'category_id',
            'supplier', 'supplier_id', 'cost_price', 'selling_price', 'margin_percentage',
            'reorder_point', 'reorder_quantity', 'max_stock', 'unit_of_measure',
            'weight', 'dimensions', 'is_active', 'is_discontinued', 'images',
            'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        """Create product with related objects."""
        images_data = validated_data.pop('images', [])
        product = Product.objects.create(**validated_data)
        
        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)
        
        return product

    def update(self, instance, validated_data):
        """Update product."""
        images_data = validated_data.pop('images', [])
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if images_data:
            instance.images.all().delete()
            for image_data in images_data:
                ProductImage.objects.create(product=instance, **image_data)
        
        return instance
