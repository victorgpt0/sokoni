from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse

from products.models import Category, Product

from .models import Wishlist


class WishlistModelTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.category = Category.objects.create(
            name="Electronics", description="Electronic devices"
        )
        self.product = Product.objects.create(
            user=self.user,
            name="Test Product",
            category=self.category,
            price=100.00,
            stock_quantity=10,
        )

    def test_wishlist_creation(self):
        """Test creating a wishlist item"""
        wishlist_item = Wishlist.objects.create(user=self.user, product=self.product)

        self.assertEqual(wishlist_item.user, self.user)
        self.assertEqual(wishlist_item.product, self.product)
        self.assertIsNotNone(wishlist_item.created_at)

    def test_wishlist_str_representation(self):
        """Test wishlist string representation"""
        wishlist_item = Wishlist.objects.create(user=self.user, product=self.product)
        expected = f"{self.user.username} - {self.product.name}"
        self.assertEqual(str(wishlist_item), expected)

    def test_wishlist_unique_constraint(self):
        """Test wishlist unique constraint on user and product"""
        Wishlist.objects.create(user=self.user, product=self.product)

        # Try to create another wishlist item with same user and product
        with self.assertRaises(IntegrityError):  # IntegrityError
            Wishlist.objects.create(user=self.user, product=self.product)

    def test_wishlist_ordering(self):
        """Test wishlist ordering by created_at (newest first)"""
        product2 = Product.objects.create(
            user=self.user,
            name="Test Product 2",
            category=self.category,
            price=200.00,
            stock_quantity=5,
        )

        wishlist_item1 = Wishlist.objects.create(user=self.user, product=self.product)

        wishlist_item2 = Wishlist.objects.create(user=self.user, product=product2)

        wishlist_items = Wishlist.objects.all()
        self.assertEqual(wishlist_items[0], wishlist_item2)  # Newest first
        self.assertEqual(wishlist_items[1], wishlist_item1)

    def test_wishlist_user_relationship(self):
        """Test wishlist-user relationship"""
        product2 = Product.objects.create(
            user=self.user,
            name="Test Product 2",
            category=self.category,
            price=200.00,
            stock_quantity=5,
        )

        wishlist_item1 = Wishlist.objects.create(user=self.user, product=self.product)

        wishlist_item2 = Wishlist.objects.create(user=self.user, product=product2)

        # Test user wishlists relationship
        self.assertEqual(self.user.wishlists.count(), 2)
        self.assertIn(wishlist_item1, self.user.wishlists.all())
        self.assertIn(wishlist_item2, self.user.wishlists.all())

    def test_wishlist_product_relationship(self):
        """Test wishlist-product relationship"""
        user2 = self.User.objects.create_user(
            username="testuser2", email="test2@example.com", password="testpass123"
        )

        wishlist_item1 = Wishlist.objects.create(user=self.user, product=self.product)

        wishlist_item2 = Wishlist.objects.create(user=user2, product=self.product)

        # Test product wishlists relationship
        self.assertEqual(self.product.wishlists.count(), 2)
        self.assertIn(wishlist_item1, self.product.wishlists.all())
        self.assertIn(wishlist_item2, self.product.wishlists.all())


class WishlistViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.category = Category.objects.create(
            name="Electronics", description="Electronic devices"
        )
        self.product = Product.objects.create(
            user=self.user,
            name="Test Product",
            category=self.category,
            price=100.00,
            stock_quantity=10,
        )

    def test_wishlist_view_authenticated(self):
        """Test wishlist view for authenticated user"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("wishlist:wishlist_list"))
        self.assertEqual(response.status_code, 200)

    def test_wishlist_view_unauthenticated(self):
        """Test wishlist view for unauthenticated user"""
        response = self.client.get(reverse("wishlist:wishlist_list"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_add_to_wishlist_view_authenticated(self):
        """Test add to wishlist view for authenticated user"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("wishlist:add_to_wishlist", args=[self.product.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect after adding to wishlist

    def test_add_to_wishlist_view_unauthenticated(self):
        """Test add to wishlist view for unauthenticated user"""
        response = self.client.post(
            reverse("wishlist:add_to_wishlist", args=[self.product.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_remove_from_wishlist_view_authenticated(self):
        """Test remove from wishlist view for authenticated user"""

        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("wishlist:remove_from_wishlist", args=[self.product.id])
        )
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after removing from wishlist

    def test_remove_from_wishlist_view_unauthenticated(self):
        """Test remove from wishlist view for unauthenticated user"""
        response = self.client.post(
            reverse("wishlist:remove_from_wishlist", args=[self.product.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login


class WishlistIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.category = Category.objects.create(
            name="Electronics", description="Electronic devices"
        )
        self.product1 = Product.objects.create(
            user=self.user,
            name="Test Product 1",
            category=self.category,
            price=100.00,
            stock_quantity=10,
        )
        self.product2 = Product.objects.create(
            user=self.user,
            name="Test Product 2",
            category=self.category,
            price=200.00,
            stock_quantity=5,
        )

    def test_complete_wishlist_flow(self):
        """Test complete wishlist add/remove flow"""
        # Login
        self.client.login(username="testuser", password="testpass123")

        # Add products to wishlist
        wishlist_item1 = Wishlist.objects.create(user=self.user, product=self.product1)

        wishlist_item2 = Wishlist.objects.create(user=self.user, product=self.product2)

        # Verify wishlist items
        self.assertEqual(self.user.wishlists.count(), 2)
        self.assertIn(wishlist_item1, self.user.wishlists.all())
        self.assertIn(wishlist_item2, self.user.wishlists.all())

        # Remove one item
        wishlist_item1.delete()

        # Verify remaining item
        self.assertEqual(self.user.wishlists.count(), 1)
        self.assertNotIn(wishlist_item1, self.user.wishlists.all())
        self.assertIn(wishlist_item2, self.user.wishlists.all())

        # recreate item1
        wishlist_item = Wishlist.objects.create(user=self.user, product=self.product1)
        self.assertIn(wishlist_item, self.user.wishlists.all())

    def test_wishlist_multiple_users_same_product(self):
        """Test multiple users can add same product to wishlist"""
        user2 = self.User.objects.create_user(
            username="testuser2", email="test2@example.com", password="testpass123"
        )

        # User 1 adds product to wishlist
        wishlist_item1 = Wishlist.objects.create(user=self.user, product=self.product1)

        # User 2 adds same product to wishlist
        wishlist_item2 = Wishlist.objects.create(user=user2, product=self.product1)

        # Verify both users have the product in their wishlist
        self.assertEqual(self.user.wishlists.count(), 1)
        self.assertEqual(user2.wishlists.count(), 1)
        self.assertEqual(self.product1.wishlists.count(), 2)

        # Verify different wishlist items
        self.assertNotEqual(wishlist_item1, wishlist_item2)
        self.assertEqual(wishlist_item1.user, self.user)
        self.assertEqual(wishlist_item2.user, user2)
        self.assertEqual(wishlist_item1.product, self.product1)
        self.assertEqual(wishlist_item2.product, self.product1)

    def test_wishlist_user_product_relationships(self):
        """Test wishlist user-product relationships"""

        # Setup: add both products to user's wishlist
        Wishlist.objects.create(user=self.user, product=self.product1)
        Wishlist.objects.create(user=self.user, product=self.product2)

        # Test user has both products in wishlist
        user_wishlist_products = [item.product for item in self.user.wishlists.all()]
        self.assertIn(self.product1, user_wishlist_products)
        self.assertIn(self.product2, user_wishlist_products)

        # Test products have user in their wishlists
        product1_wishlist_users = [item.user for item in self.product1.wishlists.all()]
        product2_wishlist_users = [item.user for item in self.product2.wishlists.all()]
        self.assertIn(self.user, product1_wishlist_users)
        self.assertIn(self.user, product2_wishlist_users)
