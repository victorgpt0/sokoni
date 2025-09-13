from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from .models import Coupon


class CouponModelTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.now = timezone.now()
        self.valid_from = self.now - timedelta(days=1)
        self.valid_to = self.now + timedelta(days=30)

    def test_coupon_creation(self):
        """Test creating a coupon"""
        coupon = Coupon.objects.create(
            code='SAVE20',
            discount_type='percentage',
            discount_value=Decimal('20.00'),
            minimum_amount=Decimal('100.00'),
            usage_limit=100,
            used_count=0,
            is_active=True,
            valid_from=self.valid_from,
            valid_to=self.valid_to
        )
        
        self.assertEqual(coupon.code, 'SAVE20')
        self.assertEqual(coupon.discount_type, 'percentage')
        self.assertEqual(coupon.discount_value, Decimal('20.00'))
        self.assertEqual(coupon.minimum_amount, Decimal('100.00'))
        self.assertEqual(coupon.usage_limit, 100)
        self.assertEqual(coupon.used_count, 0)
        self.assertTrue(coupon.is_active)
        self.assertEqual(coupon.valid_from, self.valid_from)
        self.assertEqual(coupon.valid_to, self.valid_to)
        self.assertIsNotNone(coupon.created_at)
        self.assertIsNotNone(coupon.updated_at)

    def test_coupon_str_representation(self):
        """Test coupon string representation"""
        coupon = Coupon.objects.create(
            code='SAVE10',
            discount_type='fixed',
            discount_value=Decimal('10.00'),
            valid_from=self.valid_from,
            valid_to=self.valid_to
        )
        expected = "Coupon SAVE10 - 10.00 Fixed"
        self.assertEqual(str(coupon), expected)

    def test_coupon_is_valid_property(self):
        """Test coupon is_valid property"""
        # Valid coupon
        valid_coupon = Coupon.objects.create(
            code='VALID20',
            discount_type='percentage',
            discount_value=Decimal('20.00'),
            is_active=True,
            valid_from=self.valid_from,
            valid_to=self.valid_to,
            usage_limit=10,
            used_count=5
        )
        self.assertTrue(valid_coupon.is_valid)
        
        # Inactive coupon
        inactive_coupon = Coupon.objects.create(
            code='INACTIVE20',
            discount_type='percentage',
            discount_value=Decimal('20.00'),
            is_active=False,
            valid_from=self.valid_from,
            valid_to=self.valid_to
        )
        self.assertFalse(inactive_coupon.is_valid)
        
        # Expired coupon
        expired_coupon = Coupon.objects.create(
            code='EXPIRED20',
            discount_type='percentage',
            discount_value=Decimal('20.00'),
            is_active=True,
            valid_from=self.now - timedelta(days=30),
            valid_to=self.now - timedelta(days=1)
        )
        self.assertFalse(expired_coupon.is_valid)
        
        # Future coupon
        future_coupon = Coupon.objects.create(
            code='FUTURE20',
            discount_type='percentage',
            discount_value=Decimal('20.00'),
            is_active=True,
            valid_from=self.now + timedelta(days=1),
            valid_to=self.now + timedelta(days=30)
        )
        self.assertFalse(future_coupon.is_valid)
        
        # Usage limit exceeded
        limit_exceeded_coupon = Coupon.objects.create(
            code='LIMIT20',
            discount_type='percentage',
            discount_value=Decimal('20.00'),
            is_active=True,
            valid_from=self.valid_from,
            valid_to=self.valid_to,
            usage_limit=5,
            used_count=5
        )
        self.assertFalse(limit_exceeded_coupon.is_valid)
