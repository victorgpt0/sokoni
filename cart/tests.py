from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import Customer
from products.models import Product

from .models import Cart, CartItem


class CartMergingTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()

        # Create a test user
        self.user = self.User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.customer = Customer.objects.create(user=self.user)

        # Create a test category
        from products.models import Category

        self.category = Category.objects.create(
            name="Test Category", description="Test Category Description"
        )

        # Create test products
        self.product1 = Product.objects.create(
            user=self.user,
            name="Test Product 1",
            description="Test Description 1",
            category=self.category,
            price=Decimal("100.00"),
            stock_quantity=10,
            is_active=True,
        )

        self.product2 = Product.objects.create(
            user=self.user,
            name="Test Product 2",
            description="Test Description 2",
            category=self.category,
            price=Decimal("200.00"),
            stock_quantity=5,
            is_active=True,
        )

    def test_anonymous_cart_creation(self):
        """Test that anonymous users can add items to cart"""
        # Add item to cart as anonymous user
        response = self.client.post(
            reverse("cart:add_to_cart"),
            data={"product_id": self.product1.id, "quantity": 2},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        # Check that anonymous cart was created
        session_key = self.client.session.session_key
        anonymous_cart = Cart.objects.get(session_key=session_key, customer=None)
        self.assertEqual(anonymous_cart.total_items, 2)

    def test_cart_merging_on_login(self):
        """Test that anonymous cart is merged with user cart on login"""
        # Add items to cart as anonymous user
        self.client.post(
            reverse("cart:add_to_cart"),
            data={"product_id": self.product1.id, "quantity": 2},
            content_type="application/json",
        )

        self.client.post(
            reverse("cart:add_to_cart"),
            data={"product_id": self.product2.id, "quantity": 1},
            content_type="application/json",
        )

        # Verify anonymous cart has items
        session_key = self.client.session.session_key
        anonymous_cart = Cart.objects.get(session_key=session_key, customer=None)
        self.assertEqual(anonymous_cart.total_items, 3)

        # Login
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "testuser", "password": "testpass123"},
        )

        self.assertEqual(response.status_code, 302)  # Redirect after login

        # Check that user cart was created and has merged items
        user_cart = Cart.objects.get(customer=self.customer)
        self.assertEqual(user_cart.total_items, 3)

        # Check that anonymous cart was deleted
        with self.assertRaises(Cart.DoesNotExist):
            Cart.objects.get(session_key=session_key, customer=None)

    def test_cart_merging_on_register(self):
        """Test that anonymous cart is merged with user cart on registration"""
        # Add items to cart as anonymous user
        self.client.post(
            reverse("cart:add_to_cart"),
            data={"product_id": self.product1.id, "quantity": 1},
            content_type="application/json",
        )

        # Register new user
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "newpass123",
                "password2": "newpass123",
                "first_name": "New",
                "last_name": "User",
            },
        )

        self.assertEqual(response.status_code, 302)  # Redirect after registration

        # Check that new user cart was created and has merged items
        new_user = self.User.objects.get(username="newuser")
        new_customer = Customer.objects.get(user=new_user)
        user_cart = Cart.objects.get(customer=new_customer)
        self.assertEqual(user_cart.total_items, 1)

    def test_cart_merging_with_existing_user_cart(self):
        """Test merging when user already has items in their cart"""
        # Create user cart with existing items
        user_cart = Cart.objects.create(customer=self.customer)
        CartItem.objects.create(cart=user_cart, product=self.product1, quantity=1)

        # Add different items to anonymous cart
        self.client.post(
            reverse("cart:add_to_cart"),
            data={"product_id": self.product2.id, "quantity": 2},
            content_type="application/json",
        )

        # Login
        self.client.post(
            reverse("accounts:login"),
            {"username": "testuser", "password": "testpass123"},
        )

        # Check that both items are in user cart
        user_cart.refresh_from_db()
        self.assertEqual(
            user_cart.total_items, 3
        )  # 1 from user cart + 2 from anonymous cart

    def test_no_cart_merging_when_no_anonymous_cart(self):
        """Test that login works normally when no anonymous cart exists"""
        # Login without any anonymous cart
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "testuser", "password": "testpass123"},
        )

        self.assertEqual(response.status_code, 302)

        # Check that user cart exists but is empty
        user_cart = Cart.objects.get(customer=self.customer)
        self.assertEqual(user_cart.total_items, 0)
