"""
Quick development seeder - sets up a complete database for development/testing.
Usage: python manage.py seed_dev
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction


class Command(BaseCommand):
    help = 'Quick setup for development - seeds all data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--small',
            action='store_true',
            help='Create smaller dataset (faster for quick testing)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing data before seeding',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.HTTP_INFO('🚀 Setting up development database...')
        )

        if options['small']:
            user_count = 10
            product_count = 25
            order_count = 15
            self.stdout.write(self.style.WARNING('Using small dataset for quick testing'))
        else:
            user_count = 25
            product_count = 50
            order_count = 30
            self.stdout.write(self.style.WARNING('Using full dataset'))

        try:
            with transaction.atomic():
                # 1. Categories (required first)
                self.stdout.write('📂 Creating categories...')
                call_command('seed_categories', clear=options['clear'], verbosity=0)
                
                # 2. Users and customers
                self.stdout.write('👥 Creating users and customer profiles...')
                call_command('seed_users', count=user_count, with_addresses=True, 
                           clear=options['clear'], verbosity=0)
                
                # 3. Products
                self.stdout.write('🛍️ Creating products...')
                call_command('seed_products', count=product_count, 
                           clear=options['clear'], verbosity=0)
                
                # 4. Coupons
                self.stdout.write('🎫 Creating discount coupons...')
                call_command('seed_coupons', clear=options['clear'], verbosity=0)
                
                # 5. Complete seeding (reviews, orders, payments)
                self.stdout.write('📦 Creating orders and reviews...')
                call_command('seed_all', users=user_count, products=product_count, 
                           orders=order_count, verbosity=0)

            self.stdout.write(
                self.style.SUCCESS('✅ Development database setup complete!')
            )
            
            # Display summary
            self.display_summary()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during seeding: {str(e)}')
            )
            raise

    def display_summary(self):
        """Display a summary of created data."""
        from django.contrib.auth.models import User
        from accounts.models import Customer, CustomerAddress
        from products.models import Category, Product, ProductReview
        from coupons.models import Coupon
        from orders.models import Order
        from payments.models import Payment

        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.HTTP_INFO('📊 DATABASE SUMMARY'))
        self.stdout.write('='*50)
        
        summary_data = [
            ('👥 Users', User.objects.filter(is_superuser=False).count()),
            ('🏠 Customer Addresses', CustomerAddress.objects.count()),
            ('📂 Categories', Category.objects.count()),
            ('🛍️ Products', Product.objects.count()),
            ('⭐ Product Reviews', ProductReview.objects.count()),
            ('🎫 Coupons', Coupon.objects.count()),
            ('📦 Orders', Order.objects.count()),
            ('💳 Payments', Payment.objects.count()),
        ]
        
        for label, count in summary_data:
            self.stdout.write(f'{label}: {count}')
        
        self.stdout.write('='*50)
        
        # Sample login info
        sample_users = User.objects.filter(is_superuser=False)[:3]
        if sample_users:
            self.stdout.write(self.style.HTTP_INFO('\n🔑 SAMPLE LOGIN CREDENTIALS:'))
            self.stdout.write('Password for all users: password123')
            for user in sample_users:
                self.stdout.write(f'  • {user.username} ({user.email})')
        
        # Sample coupons
        active_coupons = Coupon.objects.filter(is_active=True)[:5]
        if active_coupons:
            self.stdout.write(self.style.HTTP_INFO('\n🎫 SAMPLE ACTIVE COUPONS:'))
            for coupon in active_coupons:
                self.stdout.write(f'  • {coupon.code}')
        
        self.stdout.write('\n🎉 Ready to start development!')
        self.stdout.write('   • Admin: /admin/')
        self.stdout.write('   • Products: /products/')
        self.stdout.write('   • Cart: /cart/')
        self.stdout.write('   • Accounts: /accounts/')
        self.stdout.write('')
