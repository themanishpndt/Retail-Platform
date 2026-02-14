"""
Management command to initialize the platform with sample data.

Usage: python manage.py init_sample_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from products.models import Category, Product, Supplier
from inventory.models import Store, InventoryLevel
from orders.models import Customer
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Initialize the platform with sample data for development'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting sample data initialization...'))

        try:
            # Create categories
            self.stdout.write('Creating product categories...')
            categories = [
                Category.objects.get_or_create(name='Electronics', defaults={'description': 'Electronic devices'}),
                Category.objects.get_or_create(name='Clothing', defaults={'description': 'Apparel and fashion'}),
                Category.objects.get_or_create(name='Groceries', defaults={'description': 'Food and beverages'}),
                Category.objects.get_or_create(name='Home & Garden', defaults={'description': 'Home and garden items'}),
            ]

            # Create suppliers
            self.stdout.write('Creating suppliers...')
            suppliers = [
                Supplier.objects.get_or_create(
                    name='TechSupply Inc',
                    defaults={
                        'email': 'contact@techsupply.com',
                        'phone': '+1-555-0101',
                        'address': '123 Tech Lane',
                        'city': 'San Francisco',
                        'country': 'USA',
                    }
                ),
                Supplier.objects.get_or_create(
                    name='FashionWorld',
                    defaults={
                        'email': 'orders@fashionworld.com',
                        'phone': '+1-555-0102',
                        'address': '456 Fashion Ave',
                        'city': 'New York',
                        'country': 'USA',
                    }
                ),
            ]

            # Create stores
            self.stdout.write('Creating stores...')
            stores = [
                Store.objects.get_or_create(
                    store_id='STORE_001',
                    defaults={
                        'name': 'Downtown Store',
                        'location': '123 Main St, New York, NY',
                        'manager': 'John Doe',
                        'email': 'downtown@retailstore.com',
                        'phone': '+1-555-0201',
                    }
                ),
                Store.objects.get_or_create(
                    store_id='STORE_002',
                    defaults={
                        'name': 'Mall Location',
                        'location': '456 Shopping Plaza, Los Angeles, CA',
                        'manager': 'Jane Smith',
                        'email': 'mall@retailstore.com',
                        'phone': '+1-555-0202',
                    }
                ),
            ]

            # Create customers
            self.stdout.write('Creating customers...')
            customers = [
                Customer.objects.get_or_create(
                    customer_id='CUST_001',
                    defaults={
                        'name': 'Alice Johnson',
                        'email': 'alice@email.com',
                        'phone': '+1-555-0301',
                        'city': 'New York',
                    }
                ),
                Customer.objects.get_or_create(
                    customer_id='CUST_002',
                    defaults={
                        'name': 'Bob Williams',
                        'email': 'bob@email.com',
                        'phone': '+1-555-0302',
                        'city': 'Los Angeles',
                    }
                ),
            ]

            self.stdout.write(self.style.SUCCESS('Sample data initialization completed!'))

        except Exception as e:
            logger.error(f"Error initializing sample data: {str(e)}")
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
