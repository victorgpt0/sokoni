"""
Management command to seed products with realistic data.
Usage: python manage.py seed_products --count 50
"""

import random
import uuid
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from products.models import Category, Product, ProductImage


class Command(BaseCommand):
    help = "Seed products with realistic data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=50,
            help="Number of products to create (default: 50)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing products before seeding",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write(self.style.WARNING("Clearing existing products..."))
            ProductImage.objects.all().delete()
            Product.objects.all().delete()

        # Check if categories exist
        categories = Category.objects.all()
        if not categories.exists():
            self.stdout.write(
                self.style.ERROR(
                    "No categories found. Please run: python manage.py seed_categories"
                )
            )
            return

        # Realistic product data organized by category
        product_data = {
            "Electronics": {
                "Smartphones": [
                    {
                        "name": "iPhone 14 Pro Max",
                        "price": 1099.99,
                        "desc": "Latest iPhone with Pro camera system and A16 Bionic chip",
                    },
                    {
                        "name": "Samsung Galaxy S23 Ultra",
                        "price": 1199.99,
                        "desc": "Premium Android phone with S Pen and 200MP camera",
                    },
                    {
                        "name": "Google Pixel 7 Pro",
                        "price": 899.99,
                        "desc": "Google's flagship with advanced AI photography",
                    },
                    {
                        "name": "OnePlus 11",
                        "price": 699.99,
                        "desc": "Fast charging flagship with Snapdragon 8 Gen 2",
                    },
                    {
                        "name": "Xiaomi 13 Pro",
                        "price": 799.99,
                        "desc": "High-performance phone with Leica cameras",
                    },
                ],
                "Laptops": [
                    {
                        "name": "MacBook Pro 14-inch M2",
                        "price": 1999.99,
                        "desc": "Professional laptop with M2 Pro chip",
                    },
                    {
                        "name": "Dell XPS 13 Plus",
                        "price": 1299.99,
                        "desc": "Ultrabook with InfinityEdge display",
                    },
                    {
                        "name": "ThinkPad X1 Carbon Gen 10",
                        "price": 1599.99,
                        "desc": "Business laptop with carbon fiber build",
                    },
                    {
                        "name": "HP Spectre x360",
                        "price": 1199.99,
                        "desc": "Convertible laptop with OLED display",
                    },
                    {
                        "name": "ASUS ZenBook Pro 15",
                        "price": 1799.99,
                        "desc": "Creator laptop with OLED ScreenPad",
                    },
                ],
                "Headphones": [
                    {
                        "name": "Sony WH-1000XM4",
                        "price": 349.99,
                        "desc": "Industry-leading noise canceling headphones",
                    },
                    {
                        "name": "Bose QuietComfort 45",
                        "price": 329.99,
                        "desc": "Comfortable noise canceling headphones",
                    },
                    {
                        "name": "AirPods Pro 2nd Gen",
                        "price": 249.99,
                        "desc": "Apple's premium wireless earbuds",
                    },
                    {
                        "name": "Sennheiser Momentum 4",
                        "price": 379.99,
                        "desc": "Audiophile wireless headphones",
                    },
                ],
                "Gaming": [
                    {
                        "name": "PlayStation 5",
                        "price": 499.99,
                        "desc": "Next-gen gaming console from Sony",
                    },
                    {
                        "name": "Xbox Series X",
                        "price": 499.99,
                        "desc": "Microsoft's flagship gaming console",
                    },
                    {
                        "name": "Nintendo Switch OLED",
                        "price": 349.99,
                        "desc": "Portable gaming console with OLED screen",
                    },
                    {
                        "name": "Steam Deck",
                        "price": 399.99,
                        "desc": "Handheld PC gaming device from Valve",
                    },
                ],
            },
            "Fashion": {
                "Men's Clothing": [
                    {
                        "name": "Levi's 501 Original Jeans",
                        "price": 89.99,
                        "desc": "Classic straight-leg jeans in timeless style",
                    },
                    {
                        "name": "Ralph Lauren Polo Shirt",
                        "price": 89.99,
                        "desc": "Premium cotton polo with iconic logo",
                    },
                    {
                        "name": "Nike Dri-FIT T-Shirt",
                        "price": 29.99,
                        "desc": "Moisture-wicking athletic shirt",
                    },
                    {
                        "name": "Adidas Ultraboost 22",
                        "price": 189.99,
                        "desc": "High-performance running shoes",
                    },
                ],
                "Women's Clothing": [
                    {
                        "name": "Zara Midi Dress",
                        "price": 59.99,
                        "desc": "Elegant midi dress for any occasion",
                    },
                    {
                        "name": "H&M Blazer",
                        "price": 79.99,
                        "desc": "Professional blazer in classic cut",
                    },
                    {
                        "name": "Uniqlo Cashmere Sweater",
                        "price": 99.99,
                        "desc": "Luxurious cashmere in multiple colors",
                    },
                ],
                "Shoes": [
                    {
                        "name": "Nike Air Force 1",
                        "price": 109.99,
                        "desc": "Iconic basketball sneakers",
                    },
                    {
                        "name": "Adidas Stan Smith",
                        "price": 79.99,
                        "desc": "Classic white tennis shoes",
                    },
                    {
                        "name": "Converse Chuck Taylor All Star",
                        "price": 64.99,
                        "desc": "Timeless canvas sneakers",
                    },
                ],
            },
            "Home & Garden": {
                "Kitchen": [
                    {
                        "name": "KitchenAid Stand Mixer",
                        "price": 429.99,
                        "desc": "Professional 5-quart stand mixer",
                    },
                    {
                        "name": "Ninja Foodi Air Fryer",
                        "price": 199.99,
                        "desc": "Multi-function air fryer and pressure cooker",
                    },
                    {
                        "name": "Vitamix Blender",
                        "price": 449.99,
                        "desc": "High-performance blender for smoothies and more",
                    },
                    {
                        "name": "Instant Pot Duo",
                        "price": 99.99,
                        "desc": "7-in-1 electric pressure cooker",
                    },
                ],
                "Furniture": [
                    {
                        "name": "IKEA MALM Bed Frame",
                        "price": 199.99,
                        "desc": "Modern bed frame with adjustable sides",
                    },
                    {
                        "name": "West Elm Mid-Century Sofa",
                        "price": 1299.99,
                        "desc": "Stylish mid-century modern sofa",
                    },
                    {
                        "name": "CB2 Dining Table",
                        "price": 799.99,
                        "desc": "Contemporary dining table for 6",
                    },
                ],
            },
            "Sports & Fitness": {
                "Fitness Equipment": [
                    {
                        "name": "Peloton Bike+",
                        "price": 2495.99,
                        "desc": "Smart exercise bike with live classes",
                    },
                    {
                        "name": "Bowflex Dumbbells",
                        "price": 549.99,
                        "desc": "Adjustable dumbbells 5-52.5 lbs",
                    },
                    {
                        "name": "NordicTrack Treadmill",
                        "price": 1999.99,
                        "desc": "Commercial-grade treadmill with iFit",
                    },
                ],
                "Outdoor Sports": [
                    {
                        "name": "Yeti Cooler 45",
                        "price": 299.99,
                        "desc": "Rotomolded cooler that keeps ice for days",
                    },
                    {
                        "name": "Patagonia Hiking Backpack",
                        "price": 189.99,
                        "desc": "30L hiking backpack with rain cover",
                    },
                ],
            },
        }

        created_count = 0

        # Get all categories for random assignment
        all_categories = list(categories)

        for i in range(options["count"]):
            # Try to get category-specific data first
            category = random.choice(all_categories)
            category_name = category.name

            # Get product template - check if we have specific data for this category
            template = None
            for _parent_name, category_dict in product_data.items():
                if category_name in category_dict:
                    templates = category_dict[category_name]
                    if templates:
                        template = random.choice(templates)
                        break

            # If no specific template found, create generic product
            if not template:
                template = self.get_generic_product(category_name, i)

            # Add variation to avoid duplicates
            variation = random.randint(1, 1000)
            if str(variation) not in template["name"]:
                name = f"{template['name']} - Model {variation}"
            else:
                name = template["name"]

            # Create the product
            try:
                product = Product.objects.create(
                    name=name,
                    slug=slugify(name)[:50],  # Ensure slug doesn't exceed field limit
                    description=self.generate_detailed_description(
                        template["desc"], category_name
                    ),
                    category=category,
                    price=Decimal(str(template["price"])),
                    compare_price=self.get_compare_price(template["price"]),
                    sku=f"SKU{uuid.uuid4().hex[:8].upper()}",
                    stock_quantity=random.randint(0, 100),
                    weight=Decimal(str(random.uniform(0.1, 5.0))),
                    dimensions=f"{random.randint(10, 50)}×{random.randint(10, 50)}×{random.randint(5, 20)} cm",
                    is_active=True,
                    is_featured=(
                        random.choice([True, False]) if random.random() < 0.3 else False
                    ),
                    meta_title=name[:60],
                    meta_description=template["desc"][:160],
                )

                # Create product images (placeholder)
                self.create_product_images(product)

                created_count += 1
                if created_count % 10 == 0:
                    self.stdout.write(f"Created {created_count} products...")

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error creating product {name}: {str(e)}")
                )
                continue

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {created_count} products")
        )

    def get_generic_product(self, category_name, index):
        """Generate a generic product for categories without specific data."""
        base_prices = {
            "Electronics": random.uniform(50, 2000),
            "Fashion": random.uniform(20, 500),
            "Home": random.uniform(30, 1000),
            "Sports": random.uniform(25, 800),
            "Books": random.uniform(10, 100),
            "Health": random.uniform(15, 200),
        }

        # Determine price range based on category
        price = random.uniform(20, 500)
        for key, value in base_prices.items():
            if key.lower() in category_name.lower():
                price = value
                break

        return {
            "name": f"{category_name} Product {index + 1}",
            "price": round(price, 2),
            "desc": f"High-quality {category_name.lower()} product with excellent features and durability.",
        }

    def get_compare_price(self, price):
        """Generate a compare price (original price before discount)."""
        if random.choice([True, False]):  # 50% chance of having a compare price
            return Decimal(str(round(price * random.uniform(1.1, 1.4), 2)))
        return None

    def generate_detailed_description(self, short_desc, category):
        """Generate a more detailed product description."""
        features = [
            "Premium quality materials and construction",
            "Designed for durability and long-lasting performance",
            "Easy to use with intuitive controls",
            "Backed by manufacturer warranty",
            "Fast and reliable customer support",
            "Environmentally friendly packaging",
            "Available in multiple colors and sizes",
            "Compatible with standard accessories",
        ]

        selected_features = random.sample(features, random.randint(3, 6))
        feature_text = "\n\nKey Features:\n• " + "\n• ".join(selected_features)

        return f"{short_desc}\n\nPerfect for {category.lower()} enthusiasts and professionals alike. This product combines innovative design with practical functionality to deliver exceptional value.{feature_text}\n\nIdeal for both personal use and as a gift for friends and family."

    def create_product_images(self, product):
        """Create placeholder product images."""
        num_images = random.randint(1, 4)
        for i in range(num_images):
            ProductImage.objects.create(
                product=product,
                image=f"products/{product.slug}/image_{i+1}.jpg",  # Placeholder path
                alt_text=f"{product.name} - Image {i+1}",
                is_primary=(i == 0),
            )
