"""
Simple test seeder to verify basic functionality.
Usage: python manage.py test_seed
"""

import random
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from accounts.models import Customer
from products.models import Category, Product


class Command(BaseCommand):
    help = "Simple test seeder"

    def handle(self, *args, **options):
        self.stdout.write("🧪 Testing basic seeding...")

        # Test category creation
        self.stdout.write("Creating test category...")
        category, created = Category.objects.get_or_create(
            name="Test Electronics",
            defaults={
                "slug": "test-electronics",
                "description": "Test electronics category",
                "is_active": True,
            },
        )
        self.stdout.write(
            f'Category: {category.name} ({"created" if created else "existing"})'
        )

        # Test user creation
        self.stdout.write("Creating test user...")
        username = f"testuser{random.randint(1000, 9999)}"
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
        )
        self.stdout.write(f"User: {user.username}")

        # Test customer creation
        self.stdout.write("Creating test customer...")
        customer = Customer.objects.create(
            user=user, phone_number="+254700123456", gender="M"
        )
        self.stdout.write(f"Customer: {customer.full_name}")

        # Test product creation
        self.stdout.write("Creating test product...")
        product = Product.objects.create(
            name="Test iPhone 15",
            category=category,
            price=Decimal("999.99"),
            stock_quantity=10,
            is_active=True,
        )
        self.stdout.write(f"Product: {product.name}")

        self.stdout.write(
            self.style.SUCCESS("✅ Basic seeding test completed successfully!")
        )

        # Cleanup
        self.stdout.write("Cleaning up test data...")
        product.delete()
        customer.delete()
        user.delete()
        if created:  # Only delete if we created it
            category.delete()

        self.stdout.write("🧹 Test cleanup completed!")
