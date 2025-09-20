import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Customer, CustomerAddress
from products.models import Category, Product

from .models import Order, OrderItem


class OrderModelTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )
        self.customer = Customer.objects.create(user=self.user)
        self.category = Category.objects.create(
            name="Electronics", description="Electronic devices"
        )
        self.product = Product.objects.create(
            user=self.user,
            name="Test Product",
            category=self.category,
            price=Decimal("99.99"),
            stock_quantity=10,
        )
        self.address = CustomerAddress.objects.create(
            customer=self.customer,
            type="shipping",
            first_name="John",
            last_name="Doe",
            address_line_1="123 Main St",
            city="New York",
            country="USA",
        )

    def test_order_creation(self):
        """Test creating an order"""
        order = Order.objects.create(
            customer=self.customer,
            status="pending",
            payment_status="pending",
            subtotal=Decimal("99.99"),
            tax_amount=Decimal("8.00"),
            shipping_cost=Decimal("5.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("112.99"),
            shipping_address=self.address,
            billing_address=self.address,
            shipping_method="standard",
            notes="Please handle with care",
        )

        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.status, "pending")
        self.assertEqual(order.payment_status, "pending")
        self.assertEqual(order.subtotal, Decimal("99.99"))
        self.assertEqual(order.tax_amount, Decimal("8.00"))
        self.assertEqual(order.shipping_cost, Decimal("5.00"))
        self.assertEqual(order.discount_amount, Decimal("0.00"))
        self.assertEqual(order.total_amount, Decimal("112.99"))
        self.assertEqual(order.shipping_address, self.address)
        self.assertEqual(order.billing_address, self.address)
        self.assertEqual(order.shipping_method, "standard")
        self.assertEqual(order.notes, "Please handle with care")
        self.assertIsNotNone(order.order_number)
        self.assertTrue(order.order_number.startswith("ORD-"))
        self.assertIsNotNone(order.created_at)
        self.assertIsNotNone(order.updated_at)

    def test_order_number_auto_generation(self):
        """Test automatic order number generation"""
        order = Order.objects.create(
            customer=self.customer,
            subtotal=Decimal("50.00"),
            total_amount=Decimal("50.00"),
        )
        self.assertTrue(order.order_number.startswith("ORD-"))
        self.assertEqual(len(order.order_number), 12)  # ORD- + 8 characters

    def test_order_str_representation(self):
        """Test order string representation"""
        order = Order.objects.create(
            customer=self.customer,
            subtotal=Decimal("100.00"),
            total_amount=Decimal("100.00"),
            status="processing",
        )
        expected = (
            f"Order {order.order_number} - {self.customer.full_name} - processing"
        )
        self.assertEqual(str(order), expected)

    def test_order_get_absolute_url(self):
        """Test order absolute URL"""
        order = Order.objects.create(
            customer=self.customer,
            subtotal=Decimal("100.00"),
            total_amount=Decimal("100.00"),
        )
        expected_url = reverse("orders:order_detail", args=[order.order_number])
        self.assertEqual(order.get_absolute_url(), expected_url)
