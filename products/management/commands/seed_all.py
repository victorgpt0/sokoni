"""
Management command to seed the database with sample data for all models.
Usage: python manage.py seed_all
"""

import random
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from accounts.models import Customer, CustomerAddress
from coupons.models import Coupon
from orders.models import Order, OrderItem
from payments.models import Payment
from products.models import Category, Product, ProductImage, ProductReview


class Command(BaseCommand):
    help = "Seed the database with sample data for all models"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before seeding",
        )
        parser.add_argument(
            "--users",
            type=int,
            default=20,
            help="Number of users to create (default: 20)",
        )
        parser.add_argument(
            "--products",
            type=int,
            default=50,
            help="Number of products to create (default: 50)",
        )
        parser.add_argument(
            "--orders",
            type=int,
            default=30,
            help="Number of orders to create (default: 30)",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write(self.style.WARNING("Clearing existing data..."))
            self.clear_data()

        with transaction.atomic():
            self.stdout.write(self.style.SUCCESS("Starting database seeding..."))

            # Create categories first
            categories = self.create_categories()
            self.stdout.write(f"Created {len(categories)} categories")

            # Create users and customers
            users = self.create_users(options["users"])
            self.stdout.write(f"Created {len(users)} users with customer profiles")

            # Create customer addresses
            addresses = self.create_addresses(users)
            self.stdout.write(f"Created {len(addresses)} customer addresses")

            # Create products
            products = self.create_products(categories, options["products"])
            self.stdout.write(f"Created {len(products)} products")

            # Create product reviews
            reviews = self.create_reviews(products, users)
            self.stdout.write(f"Created {len(reviews)} product reviews")

            # Create coupons
            # coupons = self.create_coupons()
            # self.stdout.write(f'Created {len(coupons)} discount coupons')

            # Create orders
            orders = self.create_orders(users, products, options["orders"])
            self.stdout.write(f"Created {len(orders)} orders")

        self.stdout.write(
            self.style.SUCCESS("Database seeding completed successfully!")
        )

    def clear_data(self):
        """Clear existing data from all models."""
        Payment.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Coupon.objects.all().delete()
        ProductReview.objects.all().delete()
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        CustomerAddress.objects.all().delete()
        Customer.objects.all().delete()
        # Don't delete superusers
        User.objects.filter(is_superuser=False).delete()

    def create_categories(self):
        """Create product categories."""
        categories_data = [
            # Electronics categories
            {"name": "Electronics", "description": "Latest electronics and gadgets"},
            {"name": "Smartphones", "description": "Mobile phones and accessories"},
            {"name": "Laptops", "description": "Laptops and notebook computers"},
            {"name": "Tablets", "description": "Tablets and iPad devices"},
            {"name": "Headphones", "description": "Audio equipment and headphones"},
            {
                "name": "Cameras",
                "description": "Digital cameras and photography equipment",
            },
            {"name": "Gaming", "description": "Gaming consoles and accessories"},
            # Fashion categories
            {"name": "Fashion", "description": "Trendy clothing and accessories"},
            {"name": "Men's Clothing", "description": "Clothing for men"},
            {"name": "Women's Clothing", "description": "Clothing for women"},
            {"name": "Shoes", "description": "Footwear for all occasions"},
            {"name": "Bags", "description": "Handbags, backpacks, and luggage"},
            {"name": "Jewelry", "description": "Fine and fashion jewelry"},
            {"name": "Watches", "description": "Timepieces and smartwatches"},
            # Home & Garden categories
            {
                "name": "Home & Garden",
                "description": "Everything for your home and garden",
            },
            {"name": "Furniture", "description": "Home and office furniture"},
            {"name": "Kitchen", "description": "Kitchen appliances and cookware"},
            {"name": "Bathroom", "description": "Bathroom fixtures and accessories"},
            {"name": "Garden Tools", "description": "Gardening tools and equipment"},
            # Sports & Fitness categories
            {
                "name": "Sports & Fitness",
                "description": "Sports equipment and fitness gear",
            },
            {
                "name": "Fitness Equipment",
                "description": "Home gym and fitness equipment",
            },
            {
                "name": "Outdoor Sports",
                "description": "Equipment for outdoor activities",
            },
            {"name": "Activewear", "description": "Athletic clothing and shoes"},
            # Other categories
            {"name": "Books & Media", "description": "Books, movies, music and more"},
            {"name": "Health & Beauty", "description": "Health and beauty products"},
            {"name": "Automotive", "description": "Car accessories and supplies"},
            {"name": "Baby & Kids", "description": "Products for babies and children"},
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data["name"],
                defaults={
                    "slug": slugify(cat_data["name"]),
                    "description": cat_data["description"],
                    "is_active": True,
                },
            )
            categories.append(category)  # Add both new and existing categories

        return categories

    def create_users(self, count):
        """Create users with customer profiles."""
        first_names = [
            "John",
            "Jane",
            "Michael",
            "Sarah",
            "David",
            "Emily",
            "Chris",
            "Ashley",
            "Matthew",
            "Jessica",
            "Andrew",
            "Amanda",
            "Joshua",
            "Stephanie",
            "Daniel",
            "Nicole",
            "Anthony",
            "Elizabeth",
            "Mark",
            "Helen",
            "Kevin",
            "Michelle",
            "Brian",
            "Kimberly",
            "Steven",
            "Donna",
            "Joseph",
            "Carol",
            "Thomas",
            "Ruth",
        ]

        last_names = [
            "Smith",
            "Johnson",
            "Williams",
            "Brown",
            "Jones",
            "Garcia",
            "Miller",
            "Davis",
            "Rodriguez",
            "Martinez",
            "Hernandez",
            "Lopez",
            "Gonzalez",
            "Wilson",
            "Anderson",
            "Thomas",
            "Taylor",
            "Moore",
            "Jackson",
            "Martin",
            "Lee",
            "Perez",
            "Thompson",
            "White",
            "Harris",
            "Sanchez",
            "Clark",
            "Ramirez",
            "Lewis",
            "Robinson",
        ]

        users = []
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}.{last_name.lower()}{i}"
            email = f"{username}@example.com"

            user = User.objects.create_user(
                username=username,
                email=email,
                password="password123",
                first_name=first_name,
                last_name=last_name,
                is_active=True,
            )

            # Create customer profile
            Customer.objects.create(
                user=user,
                phone_number=f"+254{random.randint(700000000, 799999999)}",
                date_of_birth=datetime(
                    random.randint(1970, 2000),
                    random.randint(1, 12),
                    random.randint(1, 28),
                ).date(),
                gender=random.choice(["M", "F", "O"]),
            )

            users.append(user)

        return users

    def create_addresses(self, users):
        """Create customer addresses."""
        kenyan_cities = [
            "Nairobi",
            "Mombasa",
            "Kisumu",
            "Nakuru",
            "Eldoret",
            "Thika",
            "Malindi",
            "Kitale",
            "Garissa",
            "Kakamega",
            "Machakos",
            "Meru",
        ]

        street_names = [
            "Kimathi Street",
            "Uhuru Highway",
            "Kenyatta Avenue",
            "Moi Avenue",
            "Harambee Avenue",
            "University Way",
            "Tom Mboya Street",
            "Jogoo Road",
            "Ngong Road",
            "Waiyaki Way",
            "Outer Ring Road",
            "Thika Road",
        ]

        addresses = []
        for user in users:
            # Create 1-3 addresses per user
            num_addresses = random.randint(1, 3)
            for i in range(num_addresses):
                address = CustomerAddress.objects.create(
                    customer=user.customer,
                    type=random.choice(["shipping", "billing"]),
                    first_name=user.first_name,
                    last_name=user.last_name,
                    address_line_1=f"{random.randint(1, 999)} {random.choice(street_names)}",
                    address_line_2=(
                        f"Apt {random.randint(1, 50)}"
                        if random.choice([True, False])
                        else ""
                    ),
                    city=random.choice(kenyan_cities),
                    state=random.choice(
                        [
                            "Nairobi",
                            "Mombasa",
                            "Kisumu",
                            "Nakuru",
                            "Uasin Gishu",
                            "Kiambu",
                            "Kilifi",
                            "Trans Nzoia",
                            "Garissa",
                            "Kakamega",
                        ]
                    ),
                    postal_code=f"{random.randint(10000, 99999)}",
                    country="Kenya",
                    is_default=(i == 0),  # First address is default
                )
                addresses.append(address)

        return addresses

    def create_products(self, categories, count):
        """Create products with images."""
        # Sample product data by category
        product_templates = {
            "Electronics": [
                {
                    "name": "iPhone 14 Pro",
                    "price": 999.99,
                    "description": "Latest iPhone with Pro camera system",
                },
                {
                    "name": "Samsung Galaxy S23",
                    "price": 899.99,
                    "description": "Flagship Android smartphone",
                },
                {
                    "name": "MacBook Air M2",
                    "price": 1199.99,
                    "description": "Apple laptop with M2 chip",
                },
                {
                    "name": "Dell XPS 13",
                    "price": 999.99,
                    "description": "Premium Windows laptop",
                },
                {
                    "name": 'iPad Pro 12.9"',
                    "price": 1099.99,
                    "description": "Professional tablet",
                },
                {
                    "name": "Sony WH-1000XM4",
                    "price": 349.99,
                    "description": "Noise-canceling headphones",
                },
                {
                    "name": "Canon EOS R5",
                    "price": 3899.99,
                    "description": "Professional mirrorless camera",
                },
                {
                    "name": "Nintendo Switch OLED",
                    "price": 349.99,
                    "description": "Gaming console",
                },
            ],
            "Fashion": [
                {
                    "name": "Levi's 501 Jeans",
                    "price": 89.99,
                    "description": "Classic straight-leg jeans",
                },
                {
                    "name": "Nike Air Max 90",
                    "price": 119.99,
                    "description": "Iconic sneakers",
                },
                {
                    "name": "Ray-Ban Aviator",
                    "price": 159.99,
                    "description": "Classic aviator sunglasses",
                },
                {
                    "name": "Polo Ralph Lauren Shirt",
                    "price": 79.99,
                    "description": "Classic polo shirt",
                },
                {
                    "name": "Coach Leather Handbag",
                    "price": 299.99,
                    "description": "Premium leather handbag",
                },
                {
                    "name": "Rolex Submariner",
                    "price": 8995.99,
                    "description": "Luxury dive watch",
                },
            ],
            "Home & Garden": [
                {
                    "name": "IKEA BILLY Bookshelf",
                    "price": 59.99,
                    "description": "Adjustable bookshelf",
                },
                {
                    "name": "KitchenAid Stand Mixer",
                    "price": 379.99,
                    "description": "Professional stand mixer",
                },
                {
                    "name": "Dyson V15 Vacuum",
                    "price": 749.99,
                    "description": "Cordless vacuum cleaner",
                },
                {
                    "name": "Weber Genesis Grill",
                    "price": 899.99,
                    "description": "Gas barbecue grill",
                },
            ],
            "Sports & Fitness": [
                {
                    "name": "Peloton Bike+",
                    "price": 2495.99,
                    "description": "Smart exercise bike",
                },
                {
                    "name": "Nike Dri-FIT T-Shirt",
                    "price": 29.99,
                    "description": "Moisture-wicking athletic shirt",
                },
                {
                    "name": "Wilson Tennis Racket",
                    "price": 129.99,
                    "description": "Professional tennis racket",
                },
                {
                    "name": "Yeti Cooler 45",
                    "price": 299.99,
                    "description": "Insulated cooler",
                },
            ],
            "Books & Media": [
                {
                    "name": "The Great Gatsby",
                    "price": 12.99,
                    "description": "Classic American novel",
                },
                {
                    "name": "Dune (4K Blu-ray)",
                    "price": 24.99,
                    "description": "Sci-fi movie in 4K",
                },
                {
                    "name": "Taylor Swift - Midnights",
                    "price": 14.99,
                    "description": "Latest album on vinyl",
                },
            ],
            "Health & Beauty": [
                {
                    "name": "CeraVe Moisturizer",
                    "price": 16.99,
                    "description": "Daily facial moisturizer",
                },
                {
                    "name": "Olaplex Hair Treatment",
                    "price": 28.99,
                    "description": "Professional hair repair",
                },
                {
                    "name": "Vitamin D3 Supplements",
                    "price": 19.99,
                    "description": "Daily vitamin supplements",
                },
            ],
        }

        products = []

        for i in range(count):
            category = random.choice(categories)
            category_name = category.name

            # Get product template - check if we have specific data for this category
            template = None
            for _parent_name, category_dict in product_templates.items():
                if category_name in category_dict:
                    templates = category_dict[category_name]
                    if templates:
                        template = random.choice(templates)
                        break

            # If no specific template found, create generic product
            if not template:
                template = {
                    "name": f"{category_name} Product {i+1}",
                    "price": random.uniform(20, 500),
                    "description": f"High-quality {category_name.lower()} product with excellent features and durability.",
                }

            # Add variation to avoid duplicates
            variation = random.randint(1, 100)
            name = f"{template['name']} - Model {variation}"

            product = Product.objects.create(
                name=name,
                slug=slugify(name),
                description=template["description"]
                + f" - Perfect for {category_name.lower()}.",
                category=category,
                price=Decimal(str(template["price"])),
                compare_price=(
                    Decimal(str(template["price"] * random.uniform(1.1, 1.5)))
                    if random.choice([True, False])
                    else None
                ),
                sku=f"SKU-{uuid.uuid4().hex[:8].upper()}",
                stock_quantity=random.randint(0, 100),
                weight=Decimal(str(random.uniform(0.1, 5.0))),
                dimensions=f"{random.randint(10, 50)}x{random.randint(10, 50)}x{random.randint(5, 20)} cm",
                is_active=True,
                is_featured=random.choice([True, False]),
                meta_title=name,
                meta_description=template["description"],
            )

            # # Create 1-3 product images (placeholder URLs)
            # for j in range(random.randint(1, 3)):
            #     ProductImage.objects.create(
            #         product=product,
            #         image=f"products/{slugify(name)}/image_{j+1}.jpg",  # Placeholder path
            #         alt_text=f"{name} - Image {j+1}",
            #         is_primary=(j == 0)
            #     )

            products.append(product)

        return products

    def create_reviews(self, products, users):
        """Create product reviews."""
        review_titles = [
            "Great product!",
            "Love it!",
            "Excellent quality",
            "Highly recommend",
            "Perfect for my needs",
            "Amazing value",
            "Outstanding service",
            "Could be better",
            "Not what I expected",
            "Decent product",
            "Fantastic purchase",
            "Really impressed",
            "Good but expensive",
            "Exactly as described",
            "Fast shipping",
        ]

        review_comments = [
            "This product exceeded my expectations. The quality is excellent and delivery was fast.",
            "Really happy with this purchase. Works exactly as advertised.",
            "Good value for money. Would definitely buy again.",
            "The product is okay but the price is a bit high for what you get.",
            "Excellent customer service and the product arrived quickly.",
            "Very satisfied with the quality and performance.",
            "The description was accurate and the product works well.",
            "Not bad but I've seen better products for the same price.",
            "Great addition to my collection. Highly recommend to others.",
            "The product is good but shipping took longer than expected.",
            "Perfect quality and exactly what I was looking for.",
            "Impressed with the build quality and attention to detail.",
            "Fair price for a decent product. Nothing spectacular.",
            "Absolutely love this! Will definitely order more.",
            "Good product overall, minor issues but nothing major.",
        ]

        reviews = []
        for product in random.sample(
            products, min(len(products), 40)
        ):  # Review 40 random products
            # Create 1-5 reviews per product
            num_reviews = random.randint(1, 5)
            reviewers = random.sample(users, min(len(users), num_reviews))

            for user in reviewers:
                review = ProductReview.objects.create(
                    product=product,
                    customer=user.customer,
                    rating=random.randint(1, 5),
                    title=random.choice(review_titles),
                    comment=random.choice(review_comments),
                )
                reviews.append(review)

        return reviews

    def create_coupons(self):
        """Create discount coupons."""
        coupons_data = [
            {
                "code": "WELCOME10",
                "description": "Welcome discount for new customers",
                "discount_type": "percentage",
                "discount_value": 10,
                "minimum_amount": 50,
                "usage_limit": 100,
            },
            {
                "code": "SAVE20",
                "description": "20% off on orders over $100",
                "discount_type": "percentage",
                "discount_value": 20,
                "minimum_amount": 100,
                "usage_limit": 50,
            },
            {
                "code": "FLAT50",
                "description": "$50 off on orders over $200",
                "discount_type": "fixed",
                "discount_value": 50,
                "minimum_amount": 200,
                "usage_limit": 25,
            },
            {
                "code": "ELECTRONICS15",
                "description": "15% off on electronics",
                "discount_type": "percentage",
                "discount_value": 15,
                "minimum_amount": 75,
                "usage_limit": 75,
            },
            {
                "code": "FREESHIP",
                "description": "Free shipping on all orders",
                "discount_type": "free_shipping",
                "discount_value": 0,
                "minimum_amount": 25,
                "usage_limit": 200,
            },
        ]

        coupons = []
        for coupon_data in coupons_data:
            coupon = Coupon.objects.create(
                code=coupon_data["code"],
                # description=coupon_data['description'],
                discount_type=coupon_data["discount_type"],
                discount_value=Decimal(str(coupon_data["discount_value"])),
                minimum_amount=Decimal(str(coupon_data["minimum_amount"])),
                usage_limit=coupon_data["usage_limit"],
                used_count=random.randint(0, coupon_data["usage_limit"] // 2),
                valid_from=datetime.now(timezone.utc) - timedelta(days=30),
                valid_to=datetime.now(timezone.utc) + timedelta(days=60),
                is_active=True,
            )
            coupons.append(coupon)

        return coupons

    def create_orders(self, users, products, count):
        """Create sample orders with items and payments."""
        orders = []

        for i in range(count):
            user = random.choice(users)
            customer = user.customer

            # Get customer addresses
            addresses = customer.addresses.all()
            if not addresses:
                continue

            shipping_address = random.choice(addresses)
            billing_address = random.choice(addresses)

            # Create order with initial values
            order = Order.objects.create(
                customer=customer,
                order_number=f"ORD-{uuid.uuid4().hex[:8].upper()}",
                status=random.choice(["pending", "processing", "shipped", "delivered"]),
                payment_status=random.choice(["pending", "paid", "failed"]),
                shipping_address=shipping_address,
                billing_address=billing_address,
                shipping_cost=Decimal("0.00"),  # Free shipping
                tax_amount=Decimal("0.00"),  # Will be calculated
                discount_amount=Decimal("0.00"),  # Will be calculated
                subtotal=Decimal("0.00"),  # Will be calculated
                total_amount=Decimal("0.00"),  # Will be calculated
                notes=f"Sample order {i+1}",
                created_at=datetime.now(timezone.utc)
                - timedelta(days=random.randint(1, 90)),
            )

            # Add 1-5 items to the order
            num_items = random.randint(1, 5)
            order_products = random.sample(products, min(len(products), num_items))

            subtotal = Decimal("0.00")
            for product in order_products:
                quantity = random.randint(1, 3)
                price = product.price

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_price=price,
                    quantity=quantity,
                )

                subtotal += price * quantity

            # Calculate totals (16% VAT in Kenya)
            tax_rate = Decimal("16.00")  # 16%
            tax_amount = subtotal * (tax_rate / 100)

            # Random discount (0-20%)
            discount_percentage = random.randint(0, 20)
            discount_amount = subtotal * (Decimal(str(discount_percentage)) / 100)

            total_amount = subtotal + tax_amount + order.shipping_cost - discount_amount

            # Update order totals
            order.subtotal = subtotal
            order.tax_amount = tax_amount
            order.discount_amount = discount_amount
            order.total_amount = total_amount
            order.save()

            # Create payment if order is paid
            if order.payment_status == "paid":
                Payment.objects.create(
                    order=order,
                    payment_method="paystack",
                    status="completed",
                    amount=total_amount,
                    paystack_reference=f"ref_{uuid.uuid4().hex[:8]}",
                    paystack_transaction_id=f"txn_{uuid.uuid4().hex[:12]}",
                    gateway_response={
                        "status": "success",
                        "message": "Payment successful",
                    },
                    paid_at=order.created_at + timedelta(minutes=random.randint(1, 30)),
                )

            orders.append(order)

        return orders
