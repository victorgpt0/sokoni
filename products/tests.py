from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import uuid
from .models import Category, Product


class CategoryModelTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_category_creation(self):
        """Test creating a category"""
        category = Category.objects.create(
            name='Electronics',
            description='Electronic devices and gadgets',
            is_active=True
        )
        
        self.assertEqual(category.name, 'Electronics')
        self.assertEqual(category.description, 'Electronic devices and gadgets')
        self.assertTrue(category.is_active)
        self.assertIsNotNone(category.slug)
        self.assertEqual(category.slug, 'electronics')
        self.assertIsNotNone(category.created_at)
        self.assertIsNotNone(category.updated_at)

    def test_category_slug_auto_generation(self):
        """Test automatic slug generation from name"""
        category = Category.objects.create(name='Home & Garden')
        self.assertEqual(category.slug, 'home-garden')

    def test_category_str_representation(self):
        """Test category string representation"""
        category = Category.objects.create(name='Books')
        self.assertEqual(str(category), 'Books')

    def test_category_get_absolute_url(self):
        """Test category absolute URL"""
        category = Category.objects.create(name='Clothing')
        expected_url = reverse('products:category_detail', args=[category.slug])
        self.assertEqual(category.get_absolute_url(), expected_url)

    def test_category_ordering(self):
        """Test category ordering by name"""
        Category.objects.create(name='Zebra')
        Category.objects.create(name='Apple')
        Category.objects.create(name='Banana')
        
        categories = Category.objects.all()
        self.assertEqual(categories[0].name, 'Apple')
        self.assertEqual(categories[1].name, 'Banana')
        self.assertEqual(categories[2].name, 'Zebra')

    def test_category_verbose_name_plural(self):
        """Test category verbose name plural"""
        self.assertEqual(Category._meta.verbose_name_plural, 'Categories')


class ProductModelTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
        )

    def test_product_creation(self):
        """Test creating a product"""
        product = Product.objects.create(
            user=self.user,
            name='iPhone 15',
            description='Latest iPhone model',
            category=self.category,
            price=Decimal('999.99'),
            compare_price=Decimal('1099.99'),
            stock_quantity=50,
            weight=Decimal('171.0'),
            dimensions='147.6 x 71.6 x 7.80 mm',
            is_active=True,
            is_featured=True,
            is_digital=False,
            meta_title='iPhone 15 - Latest Apple Phone',
            meta_description='Buy the latest iPhone 15 with advanced features',
            meta_keywords='iphone, apple, smartphone, mobile'
        )
        
        self.assertEqual(product.user, self.user)
        self.assertEqual(product.name, 'iPhone 15')
        self.assertEqual(product.description, 'Latest iPhone model')
        self.assertEqual(product.category, self.category)
        self.assertEqual(product.price, Decimal('999.99'))
        self.assertEqual(product.compare_price, Decimal('1099.99'))
        self.assertEqual(product.stock_quantity, 50)
        self.assertEqual(product.weight, Decimal('171.0'))
        self.assertEqual(product.dimensions, '147.6 x 71.6 x 7.80 mm')
        self.assertTrue(product.is_active)
        self.assertTrue(product.is_featured)
        self.assertFalse(product.is_digital)
        self.assertEqual(product.meta_title, 'iPhone 15 - Latest Apple Phone')
        self.assertIsNotNone(product.slug)
        self.assertIsNotNone(product.sku)
        self.assertIsNotNone(product.created_at)
        self.assertIsNotNone(product.updated_at)

    def test_product_slug_auto_generation(self):
        """Test automatic slug generation from name"""
        product = Product.objects.create(
            user=self.user,
            name='Samsung Galaxy S24',
            category=self.category,
            price=Decimal('799.99'),
            stock_quantity=30
        )
        self.assertEqual(product.slug, 'samsung-galaxy-s24')

    def test_product_sku_auto_generation(self):
        """Test automatic SKU generation"""
        product = Product.objects.create(
            user=self.user,
            name='Test Product',
            category=self.category,
            price=Decimal('99.99'),
            stock_quantity=10
        )
        self.assertTrue(product.sku.startswith('PRD-'))
        self.assertEqual(len(product.sku), 12)  # PRD- + 8 characters

    def test_product_str_representation(self):
        """Test product string representation"""
        product = Product.objects.create(
            user=self.user,
            name='MacBook Pro',
            category=self.category,
            price=Decimal('1999.99'),
            stock_quantity=20
        )
        self.assertEqual(str(product), 'MacBook Pro')

    def test_product_get_absolute_url(self):
        """Test product absolute URL"""
        product = Product.objects.create(
            user=self.user,
            name='iPad Air',
            category=self.category,
            price=Decimal('599.99'),
            stock_quantity=15
        )
        expected_url = reverse('products:product_detail', args=[product.slug])
        self.assertEqual(product.get_absolute_url(), expected_url)

    def test_product_is_on_sale_property(self):
        """Test product is_on_sale property"""
        # Product with compare_price > price (on sale)
        product_on_sale = Product.objects.create(
            user=self.user,
            name='Product On Sale',
            category=self.category,
            price=Decimal('100.00'),
            compare_price=Decimal('150.00'),
            stock_quantity=10
        )
        self.assertTrue(product_on_sale.is_on_sale)
        
        # Product without compare_price (not on sale)
        product_not_on_sale = Product.objects.create(
            user=self.user,
            name='Product Not On Sale',
            category=self.category,
            price=Decimal('100.00'),
            stock_quantity=10
        )
        self.assertFalse(product_not_on_sale.is_on_sale)

    def test_product_discount_percentage_property(self):
        """Test product discount_percentage property"""
        product = Product.objects.create(
            user=self.user,
            name='Discounted Product',
            category=self.category,
            price=Decimal('80.00'),
            compare_price=Decimal('100.00'),
            stock_quantity=10
        )
        expected_discount = round((100 - 80) / 100 * 100, 2)
        self.assertEqual(product.discount_percentage, expected_discount)

    def test_product_is_in_stock_property(self):
        """Test product is_in_stock property"""
        # Product in stock
        product_in_stock = Product.objects.create(
            user=self.user,
            name='In Stock Product',
            category=self.category,
            price=Decimal('50.00'),
            stock_quantity=5
        )
        self.assertTrue(product_in_stock.is_in_stock)
        
        # Product out of stock
        product_out_of_stock = Product.objects.create(
            user=self.user,
            name='Out of Stock Product',
            category=self.category,
            price=Decimal('50.00'),
            stock_quantity=0
        )
        self.assertFalse(product_out_of_stock.is_in_stock)

    def test_product_ordering(self):
        """Test product ordering by created_at (newest first)"""
        product1 = Product.objects.create(
            user=self.user,
            name='First Product',
            category=self.category,
            price=Decimal('100.00'),
            stock_quantity=10
        )
        
        product2 = Product.objects.create(
            user=self.user,
            name='Second Product',
            category=self.category,
            price=Decimal('200.00'),
            stock_quantity=20
        )
        
        products = Product.objects.all()
        self.assertEqual(products[0], product2)  # Newest first
        self.assertEqual(products[1], product1)

    def test_product_verbose_name_plural(self):
        """Test product verbose name plural"""
        self.assertEqual(Product._meta.verbose_name_plural, 'Products')
