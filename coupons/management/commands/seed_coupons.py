"""
Management command to seed discount coupons.
Usage: python manage.py seed_coupons
"""

import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from django.core.management.base import BaseCommand

from coupons.models import Coupon


class Command(BaseCommand):
    help = "Seed discount coupons"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing coupons before seeding",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write(self.style.WARNING("Clearing existing coupons..."))
            Coupon.objects.all().delete()

        coupons_data = [
            # Welcome coupons
            {
                "code": "WELCOME10",
                "description": "Welcome discount for new customers - 10% off your first order",
                "discount_type": "percentage",
                "discount_value": 10,
                "minimum_amount": 50,
                "maximum_discount": 100,
                "usage_limit": 500,
                "days_valid": 90,
            },
            {
                "code": "NEWBIE20",
                "description": "20% off for first-time shoppers on orders over $75",
                "discount_type": "percentage",
                "discount_value": 20,
                "minimum_amount": 75,
                "maximum_discount": 150,
                "usage_limit": 200,
                "days_valid": 60,
            },
            # Percentage discounts
            {
                "code": "SAVE15",
                "description": "15% off on all products - Limited time offer",
                "discount_type": "percentage",
                "discount_value": 15,
                "minimum_amount": 100,
                "maximum_discount": 200,
                "usage_limit": 1000,
                "days_valid": 30,
            },
            {
                "code": "BIGDEAL25",
                "description": "25% off on orders over $200 - Best deal of the month",
                "discount_type": "percentage",
                "discount_value": 25,
                "minimum_amount": 200,
                "maximum_discount": 500,
                "usage_limit": 100,
                "days_valid": 15,
            },
            {
                "code": "MEGA30",
                "description": "30% off on orders over $300 - Mega savings event",
                "discount_type": "percentage",
                "discount_value": 30,
                "minimum_amount": 300,
                "maximum_discount": 1000,
                "usage_limit": 50,
                "days_valid": 7,
            },
            # Fixed amount discounts
            {
                "code": "FLAT50",
                "description": "$50 off on orders over $200 - Flat discount",
                "discount_type": "fixed",
                "discount_value": 50,
                "minimum_amount": 200,
                "maximum_discount": 50,
                "usage_limit": 200,
                "days_valid": 45,
            },
            {
                "code": "SAVE100",
                "description": "$100 off on orders over $400 - Big savings",
                "discount_type": "fixed",
                "discount_value": 100,
                "minimum_amount": 400,
                "maximum_discount": 100,
                "usage_limit": 75,
                "days_valid": 30,
            },
            {
                "code": "CASH25",
                "description": "$25 off on any order over $100",
                "discount_type": "fixed",
                "discount_value": 25,
                "minimum_amount": 100,
                "maximum_discount": 25,
                "usage_limit": 300,
                "days_valid": 60,
            },
            # Category-specific coupons
            {
                "code": "ELECTRONICS20",
                "description": "20% off on all electronics - Tech sale",
                "discount_type": "percentage",
                "discount_value": 20,
                "minimum_amount": 100,
                "maximum_discount": 300,
                "usage_limit": 150,
                "days_valid": 21,
            },
            {
                "code": "FASHION15",
                "description": "15% off on fashion items - Style savings",
                "discount_type": "percentage",
                "discount_value": 15,
                "minimum_amount": 75,
                "maximum_discount": 150,
                "usage_limit": 250,
                "days_valid": 30,
            },
            {
                "code": "HOMEANDGARDEN",
                "description": "12% off on home and garden products",
                "discount_type": "percentage",
                "discount_value": 12,
                "minimum_amount": 80,
                "maximum_discount": 120,
                "usage_limit": 200,
                "days_valid": 45,
            },
            # Free shipping coupons
            {
                "code": "FREESHIP",
                "description": "Free shipping on all orders over $25",
                "discount_type": "fixed",
                "discount_value": 0,
                "minimum_amount": 25,
                "maximum_discount": 0,
                "usage_limit": 1000,
                "days_valid": 120,
            },
            {
                "code": "SHIPFREE50",
                "description": "Free shipping + $5 off on orders over $50",
                "discount_type": "fixed",
                "discount_value": 5,
                "minimum_amount": 50,
                "maximum_discount": 5,
                "usage_limit": 500,
                "days_valid": 90,
            },
            # Holiday/seasonal coupons
            {
                "code": "HOLIDAY2024",
                "description": "Holiday special - 22% off everything",
                "discount_type": "percentage",
                "discount_value": 22,
                "minimum_amount": 60,
                "maximum_discount": 250,
                "usage_limit": 300,
                "days_valid": 45,
            },
            {
                "code": "NEWYEAR2024",
                "description": "New Year savings - $75 off orders over $350",
                "discount_type": "fixed",
                "discount_value": 75,
                "minimum_amount": 350,
                "maximum_discount": 75,
                "usage_limit": 100,
                "days_valid": 30,
            },
            # VIP/Premium coupons
            {
                "code": "VIP35",
                "description": "VIP exclusive - 35% off for premium customers",
                "discount_type": "percentage",
                "discount_value": 35,
                "minimum_amount": 250,
                "maximum_discount": 500,
                "usage_limit": 25,
                "days_valid": 60,
            },
            {
                "code": "PREMIUM150",
                "description": "Premium member special - $150 off orders over $500",
                "discount_type": "fixed",
                "discount_value": 150,
                "minimum_amount": 500,
                "maximum_discount": 150,
                "usage_limit": 30,
                "days_valid": 45,
            },
            # Flash sale coupons
            {
                "code": "FLASH40",
                "description": "Flash sale - 40% off (Limited time)",
                "discount_type": "percentage",
                "discount_value": 40,
                "minimum_amount": 150,
                "maximum_discount": 400,
                "usage_limit": 50,
                "days_valid": 3,
            },
            {
                "code": "LIGHTNING",
                "description": "Lightning deal - 50% off first 20 orders",
                "discount_type": "percentage",
                "discount_value": 50,
                "minimum_amount": 100,
                "maximum_discount": 300,
                "usage_limit": 20,
                "days_valid": 1,
            },
        ]

        created_count = 0
        now = datetime.now(timezone.utc)

        for coupon_data in coupons_data:
            # Calculate validity dates
            valid_from = now - timedelta(
                days=random.randint(0, 30)
            )  # Some already started
            valid_until = valid_from + timedelta(days=coupon_data["days_valid"])

            # Some coupons should be expired for testing
            if random.random() < 0.1:  # 10% chance of expired coupon
                valid_until = now - timedelta(days=random.randint(1, 30))

            # Some coupons should be future dated
            if random.random() < 0.1:  # 10% chance of future coupon
                valid_from = now + timedelta(days=random.randint(1, 30))
                valid_until = valid_from + timedelta(days=coupon_data["days_valid"])

            try:
                coupon = Coupon.objects.create(
                    code=coupon_data["code"],
                    discount_type=coupon_data["discount_type"],
                    discount_value=Decimal(str(coupon_data["discount_value"])),
                    minimum_amount=Decimal(str(coupon_data["minimum_amount"])),
                    usage_limit=coupon_data["usage_limit"],
                    used_count=random.randint(
                        0, min(coupon_data["usage_limit"] // 3, 50)
                    ),  # Some usage
                    valid_from=valid_from,
                    valid_to=valid_until,
                    is_active=random.choice([True, True, True, False]),  # 75% active
                )

                created_count += 1
                self.stdout.write(
                    f"Created coupon: {coupon.code} ({coupon.get_discount_type_display()})"
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error creating coupon {coupon_data["code"]}: {str(e)}'
                    )
                )
                continue

        # Create some additional random coupons
        self.create_random_coupons()

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {created_count} coupons")
        )

    def create_random_coupons(self):
        """Create additional random coupons for variety."""
        random_codes = [
            "SAVE5NOW",
            "DEAL10",
            "LUCKY15",
            "BONUS20",
            "EXTRA25",
            "SUPER30",
            "QUICK5",
            "FAST10",
            "RUSH15",
            "SPEED20",
            "TURBO25",
            "ZOOM30",
        ]

        for code in random_codes:
            if Coupon.objects.filter(code=code).exists():
                continue

            discount_type = random.choice(["percentage", "fixed"])

            if discount_type == "percentage":
                discount_value = random.choice([5, 8, 10, 12, 15, 18, 20])
                minimum_amount = random.choice([25, 50, 75, 100, 150])
                maximum_discount = discount_value * 10
            else:  # fixed
                discount_value = random.choice([10, 15, 20, 25, 30, 40, 50])
                minimum_amount = discount_value * 3
                maximum_discount = discount_value

            try:
                now = datetime.now(timezone.utc)
                valid_from = now - timedelta(days=random.randint(0, 15))
                valid_until = valid_from + timedelta(days=random.randint(15, 90))

                Coupon.objects.create(
                    code=code,
                    discount_type=discount_type,
                    discount_value=Decimal(str(discount_value)),
                    minimum_amount=Decimal(str(minimum_amount)),
                    usage_limit=random.randint(50, 500),
                    used_count=random.randint(0, 25),
                    valid_from=valid_from,
                    valid_to=valid_until,
                    is_active=True,
                )

            except Exception as e:
                continue  # Skip if error
