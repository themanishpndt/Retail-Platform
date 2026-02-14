"""
Tests for product models.
"""

import pytest
from django.test import TestCase
from products.models import Category, Supplier, Product


@pytest.mark.django_db
class TestProductModel(TestCase):
    """Test Product model."""

    def setUp(self):
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
        )
        self.supplier = Supplier.objects.create(
            name='Tech Supplier',
            email='tech@supplier.com',
            phone='555-1234',
            address='123 Tech St',
            city='San Francisco',
            country='USA'
        )

    def test_create_product(self):
        """Test creating a product."""
        product = Product.objects.create(
            sku='PROD-001',
            name='Laptop',
            category=self.category,
            supplier=self.supplier,
            cost_price=500.00,
            selling_price=800.00
        )
        
        assert product.sku == 'PROD-001'
        assert product.name == 'Laptop'
        assert product.margin_percentage == 60.0

    def test_calculate_margin(self):
        """Test margin calculation."""
        product = Product.objects.create(
            sku='PROD-002',
            name='Monitor',
            category=self.category,
            cost_price=100.00,
            selling_price=150.00
        )
        
        product.calculate_margin()
        assert product.margin_percentage == 50.0

    def test_product_string_representation(self):
        """Test product string representation."""
        product = Product.objects.create(
            sku='PROD-003',
            name='Keyboard',
            category=self.category
        )
        
        assert str(product) == 'PROD-003 - Keyboard'


@pytest.mark.django_db
class TestCategoryModel(TestCase):
    """Test Category model."""

    def test_create_category(self):
        """Test creating a category."""
        category = Category.objects.create(
            name='Clothing',
            description='Apparel and fashion'
        )
        
        assert category.name == 'Clothing'

    def test_category_ordering(self):
        """Test category ordering."""
        Category.objects.create(name='B Category')
        Category.objects.create(name='A Category')
        
        categories = Category.objects.all()
        assert categories[0].name == 'A Category'
