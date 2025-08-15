"""
Management command to seed product categories.
Usage: python manage.py seed_categories
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from products.models import Category


class Command(BaseCommand):
    help = 'Seed product categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing categories before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing categories...'))
            Category.objects.all().delete()

        categories_data = [
            # Electronics categories
            {'name': 'Electronics', 'description': 'Latest electronics and gadgets'},
            {'name': 'Smartphones', 'description': 'Mobile phones and accessories'},
            {'name': 'Laptops', 'description': 'Laptops and notebook computers'},
            {'name': 'Tablets', 'description': 'Tablets and iPad devices'},
            {'name': 'Headphones', 'description': 'Audio equipment and headphones'},
            {'name': 'Cameras', 'description': 'Digital cameras and photography equipment'},
            {'name': 'Gaming', 'description': 'Gaming consoles and accessories'},
            {'name': 'Smart Home', 'description': 'Smart home devices and automation'},
            
            # Fashion categories
            {'name': 'Fashion', 'description': 'Trendy clothing and accessories'},
            {'name': 'Men\'s Clothing', 'description': 'Clothing for men'},
            {'name': 'Women\'s Clothing', 'description': 'Clothing for women'},
            {'name': 'Shoes', 'description': 'Footwear for all occasions'},
            {'name': 'Bags', 'description': 'Handbags, backpacks, and luggage'},
            {'name': 'Jewelry', 'description': 'Fine and fashion jewelry'},
            {'name': 'Watches', 'description': 'Timepieces and smartwatches'},
            {'name': 'Sunglasses', 'description': 'Designer and sport sunglasses'},
            
            # Home & Garden categories
            {'name': 'Home & Garden', 'description': 'Everything for your home and garden'},
            {'name': 'Furniture', 'description': 'Home and office furniture'},
            {'name': 'Kitchen', 'description': 'Kitchen appliances and cookware'},
            {'name': 'Bathroom', 'description': 'Bathroom fixtures and accessories'},
            {'name': 'Decor', 'description': 'Home decor and accessories'},
            {'name': 'Garden Tools', 'description': 'Gardening tools and equipment'},
            {'name': 'Outdoor', 'description': 'Outdoor furniture and equipment'},
            {'name': 'Storage', 'description': 'Storage solutions and organizers'},
            
            # Sports & Fitness categories
            {'name': 'Sports & Fitness', 'description': 'Sports equipment and fitness gear'},
            {'name': 'Fitness Equipment', 'description': 'Home gym and fitness equipment'},
            {'name': 'Outdoor Sports', 'description': 'Equipment for outdoor activities'},
            {'name': 'Team Sports', 'description': 'Equipment for team sports'},
            {'name': 'Water Sports', 'description': 'Equipment for water activities'},
            {'name': 'Winter Sports', 'description': 'Equipment for winter sports'},
            {'name': 'Activewear', 'description': 'Athletic clothing and shoes'},
            
            # Books & Media categories
            {'name': 'Books & Media', 'description': 'Books, movies, music and more'},
            {'name': 'Fiction', 'description': 'Fiction books and novels'},
            {'name': 'Non-Fiction', 'description': 'Non-fiction and educational books'},
            {'name': 'Movies', 'description': 'DVDs, Blu-rays, and digital movies'},
            {'name': 'Music', 'description': 'CDs, vinyl, and digital music'},
            {'name': 'Games', 'description': 'Video games and board games'},
            
            # Health & Beauty categories
            {'name': 'Health & Beauty', 'description': 'Health and beauty products'},
            {'name': 'Skincare', 'description': 'Skincare products and treatments'},
            {'name': 'Makeup', 'description': 'Cosmetics and beauty tools'},
            {'name': 'Hair Care', 'description': 'Hair care products and tools'},
            {'name': 'Personal Care', 'description': 'Personal hygiene products'},
            {'name': 'Health Supplements', 'description': 'Vitamins and health supplements'},
            
            # Additional categories
            {'name': 'Automotive', 'description': 'Car accessories and supplies'},
            {'name': 'Baby & Kids', 'description': 'Products for babies and children'},
            {'name': 'Pet Supplies', 'description': 'Food and accessories for pets'},
            {'name': 'Office Supplies', 'description': 'Office equipment and stationery'},
            {'name': 'Travel', 'description': 'Travel gear and accessories'}
        ]

        created_count = 0
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'description': cat_data['description'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created category: {category.name}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} categories')
        )
