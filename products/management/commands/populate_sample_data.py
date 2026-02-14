"""
Management command to populate database with sample data
Usage: python manage.py populate_sample_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

from products.models import Category, Supplier, Product
from inventory.models import Store, InventoryLevel
from orders.models import Customer, Order, OrderLine


class Command(BaseCommand):
    help = 'Populates the database with sample data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting to populate sample data...'))

        # Create Categories
        categories = []
        category_names = ['Electronics', 'Clothing', 'Food & Beverage', 'Home & Garden', 'Sports']
        for name in category_names:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'description': f'{name} products'}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {name}')

        # Create Suppliers
        suppliers = []
        supplier_names = ['Supplier A', 'Supplier B', 'Supplier C', 'Supplier D']
        for name in supplier_names:
            supplier, created = Supplier.objects.get_or_create(
                name=name,
                defaults={
                    'contact_person': f'Contact {name}',
                    'email': f'{name.lower().replace(" ", "")}@example.com',
                    'phone': f'+1-555-{random.randint(1000, 9999)}',
                    'address': f'{random.randint(100, 999)} Industrial Blvd',
                    'city': 'Sample City',
                    'country': 'USA'
                }
            )
            suppliers.append(supplier)
            if created:
                self.stdout.write(f'Created supplier: {name}')

        # Create Stores
        stores = []
        store_names = ['Main Store', 'North Branch', 'South Branch', 'Warehouse']
        for i, name in enumerate(store_names):
            store, created = Store.objects.get_or_create(
                store_id=f'STORE{i+1:03d}',
                defaults={
                    'name': name,
                    'location': f'{random.randint(100, 999)} Main St, Sample City, CA',
                    'manager': f'Manager {i+1}',
                    'email': f'store{i+1}@example.com',
                    'phone': f'+1-555-{random.randint(1000, 9999)}',
                    'is_active': True
                }
            )
            stores.append(store)
            if created:
                self.stdout.write(f'Created store: {name}')

        # Create Products
        products = []
        product_names = [
            'Laptop Pro', 'Wireless Mouse', 'USB Cable', 'Monitor 27"', 'Keyboard Mechanical',
            'T-Shirt Cotton', 'Jeans Blue', 'Sneakers Sport', 'Jacket Winter', 'Socks Pack',
            'Coffee Beans', 'Green Tea', 'Chocolate Bar', 'Orange Juice', 'Mineral Water',
            'Garden Tools Set', 'Flower Pot', 'LED Bulbs', 'Paint Brushes', 'Cleaning Spray',
            'Basketball', 'Tennis Racket', 'Yoga Mat', 'Dumbbells 5kg', 'Resistance Bands'
        ]

        for i, name in enumerate(product_names):
            category = random.choice(categories)
            supplier = random.choice(suppliers)
            
            cost = Decimal(random.uniform(5, 200))
            selling_price = cost * Decimal(random.uniform(1.2, 2.0))
            
            product, created = Product.objects.get_or_create(
                sku=f'SKU{i+1000}',
                defaults={
                    'name': name,
                    'description': f'High quality {name.lower()}',
                    'category': category,
                    'supplier': supplier,
                    'cost_price': round(cost, 2),
                    'selling_price': round(selling_price, 2),
                    'reorder_point': random.randint(10, 50),
                    'is_active': True
                }
            )
            products.append(product)
            if created:
                self.stdout.write(f'Created product: {name}')

        # Create Inventory Levels
        for product in products:
            for store in stores:
                quantity = random.randint(0, 200)
                reserved = min(random.randint(0, 30), quantity)
                
                InventoryLevel.objects.get_or_create(
                    product=product,
                    store=store,
                    defaults={
                        'quantity_on_hand': quantity,
                        'quantity_reserved': reserved,
                        'quantity_available': quantity - reserved
                    }
                )
        
        self.stdout.write(self.style.SUCCESS(f'Created inventory levels for all products'))

        # Create Customers
        customers = []
        customer_names = [
            'John Smith', 'Jane Doe', 'Bob Johnson', 'Alice Williams', 'Charlie Brown',
            'Diana Prince', 'Eve Adams', 'Frank Miller', 'Grace Lee', 'Henry Wilson'
        ]
        
        for i, name in enumerate(customer_names):
            customer, created = Customer.objects.get_or_create(
                customer_id=f'CUST{i+1:05d}',
                defaults={
                    'name': name,
                    'email': f'{name.lower().replace(" ", ".")}@example.com',
                    'phone': f'+1-555-{random.randint(1000, 9999)}',
                    'address': f'{random.randint(100, 999)} Oak St',
                    'city': 'Sample City',
                    'loyalty_points': random.randint(0, 1000)
                }
            )
            customers.append(customer)
            if created:
                self.stdout.write(f'Created customer: {name}')

        # Create Orders (last 60 days)
        order_statuses = ['CONFIRMED', 'PENDING', 'SHIPPED', 'DELIVERED']
        # Start from existing order count to avoid duplicates
        existing_orders = Order.objects.count()
        order_counter = existing_orders + 1
        
        self.stdout.write(f'Starting orders from #{order_counter}')
        
        for day in range(60):
            orders_per_day = random.randint(2, 8)
            order_date = timezone.now() - timedelta(days=day)
            
            for _ in range(orders_per_day):
                customer = random.choice(customers)
                store = random.choice(stores)
                status = random.choice(order_statuses)
                
                # Calculate order totals first
                num_items = random.randint(1, 5)
                order_products = random.sample(products, min(num_items, len(products)))
                
                subtotal = Decimal('0.00')
                for product in order_products:
                    quantity = random.randint(1, 3)
                    unit_price = product.selling_price
                    line_subtotal = unit_price * quantity
                    subtotal += line_subtotal
                
                # Calculate totals
                tax = subtotal * Decimal('0.08')  # 8% tax
                discount = Decimal('0.00')
                total = subtotal + tax - discount
                
                # Create order with all required fields
                order = Order.objects.create(
                    order_id=f'ORD{order_counter:06d}',
                    customer=customer,
                    store=store,
                    order_date=order_date,
                    status=status,
                    subtotal=subtotal,
                    tax=tax,
                    discount=discount,
                    total=total
                )
                order_counter += 1
                
                # Now add order lines
                for product in order_products:
                    quantity = random.randint(1, 3)
                    unit_price = product.selling_price
                    line_total = unit_price * quantity
                    
                    OrderLine.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        unit_price=unit_price,
                        line_total=line_total
                    )
        
        self.stdout.write(self.style.SUCCESS(f'Created {order_counter-1} orders for last 60 days'))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== Summary ==='))
        self.stdout.write(f'Categories: {Category.objects.count()}')
        self.stdout.write(f'Suppliers: {Supplier.objects.count()}')
        self.stdout.write(f'Stores: {Store.objects.count()}')
        self.stdout.write(f'Products: {Product.objects.count()}')
        self.stdout.write(f'Inventory Levels: {InventoryLevel.objects.count()}')
        self.stdout.write(f'Customers: {Customer.objects.count()}')
        self.stdout.write(f'Orders: {Order.objects.count()}')
        self.stdout.write(f'Order Lines: {OrderLine.objects.count()}')
        
        self.stdout.write(self.style.SUCCESS('\nSample data populated successfully!'))
