from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from .models import Customer, CustomerAddress


class CustomerModelTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )

    def test_customer_creation(self):
        """Test creating a customer"""
        customer = Customer.objects.create(
            user=self.user,
            phone_number='+1234567890',
            date_of_birth=timezone.now().date(),
            gender='M'
        )
        
        self.assertEqual(customer.user, self.user)
        self.assertEqual(customer.phone_number, '+1234567890')
        self.assertEqual(customer.gender, 'M')
        self.assertIsNotNone(customer.created_at)
        self.assertIsNotNone(customer.updated_at)

    def test_customer_str_representation(self):
        """Test customer string representation"""
        customer = Customer.objects.create(user=self.user)
        expected = f"{self.user.first_name} {self.user.last_name}"
        self.assertEqual(str(customer), expected)

    def test_customer_full_name_property(self):
        """Test customer full_name property"""
        customer = Customer.objects.create(user=self.user)
        expected = f"{self.user.first_name} {self.user.last_name}".strip()
        self.assertEqual(customer.full_name, expected)

    def test_customer_full_name_with_empty_names(self):
        """Test customer full_name property with empty first/last names"""
        user = self.User.objects.create_user(
            username='emptyuser',
            email='empty@example.com',
            password='testpass123'
        )
        customer = Customer.objects.create(user=user)
        self.assertEqual(customer.full_name, '')


class CustomerAddressModelTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(user=self.user)

    def test_customer_address_creation(self):
        """Test creating a customer address"""
        address = CustomerAddress.objects.create(
            customer=self.customer,
            type='shipping',
            first_name='John',
            last_name='Doe',
            company='Test Company',
            address_line_1='123 Main St',
            address_line_2='Apt 4B',
            city='New York',
            state='NY',
            postal_code='10001',
            country='USA',
            is_default=True
        )
        
        self.assertEqual(address.customer, self.customer)
        self.assertEqual(address.type, 'shipping')
        self.assertEqual(address.first_name, 'John')
        self.assertEqual(address.last_name, 'Doe')
        self.assertEqual(address.company, 'Test Company')
        self.assertEqual(address.address_line_1, '123 Main St')
        self.assertEqual(address.address_line_2, 'Apt 4B')
        self.assertEqual(address.city, 'New York')
        self.assertEqual(address.state, 'NY')
        self.assertEqual(address.postal_code, '10001')
        self.assertEqual(address.country, 'USA')
        self.assertTrue(address.is_default)

    def test_customer_address_str_representation(self):
        """Test customer address string representation"""
        address = CustomerAddress.objects.create(
            customer=self.customer,
            type='billing',
            first_name='Jane',
            last_name='Smith',
            address_line_1='456 Oak Ave',
            city='Los Angeles',
            country='USA'
        )
        expected = "Jane Smith - Los Angeles - Billing Address"
        self.assertEqual(str(address), expected)

    def test_customer_address_choices(self):
        """Test customer address type choices"""
        # Test billing address
        billing_address = CustomerAddress.objects.create(
            customer=self.customer,
            type='billing',
            first_name='John',
            last_name='Doe',
            address_line_1='123 Main St',
            city='New York',
            country='USA'
        )
        self.assertEqual(billing_address.type, 'billing')
        
        # Test shipping address
        shipping_address = CustomerAddress.objects.create(
            customer=self.customer,
            type='shipping',
            first_name='John',
            last_name='Doe',
            address_line_1='123 Main St',
            city='New York',
            country='USA'
        )
        self.assertEqual(shipping_address.type, 'shipping')


class CustomerViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        self.customer = Customer.objects.create(user=self.user)

    def test_login_view_get(self):
        """Test login view GET request"""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'login')

    def test_login_view_post_success(self):
        """Test successful login"""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login

    def test_login_view_post_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'login')

    def test_register_view_get(self):
        """Test register view GET request"""
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'register')

    def test_register_view_post_success(self):
        """Test successful user registration"""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after registration
        
        # Check that user was created
        self.assertTrue(self.User.objects.filter(username='newuser').exists())
        
        # Check that customer was created
        new_user = self.User.objects.get(username='newuser')
        self.assertTrue(Customer.objects.filter(user=new_user).exists())

    def test_register_view_post_password_mismatch(self):
        """Test registration with password mismatch"""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'differentpass',
            'first_name': 'New',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.User.objects.filter(username='newuser').exists())

    def test_logout_view(self):
        """Test logout functionality"""
        # Login first
        self.client.login(username='testuser', password='testpass123')
        
        # Logout
        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout

    def test_profile_view_authenticated(self):
        """Test profile view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)

    def test_profile_view_unauthenticated(self):
        """Test profile view for unauthenticated user"""
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_password_change_view_authenticated(self):
        """Test password change view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:password_change'))
        self.assertEqual(response.status_code, 200)

    def test_password_change_view_unauthenticated(self):
        """Test password change view for unauthenticated user"""
        response = self.client.get(reverse('accounts:password_change'))
        self.assertEqual(response.status_code, 302)  # Redirect to login


class CustomerIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()

    def test_complete_user_registration_flow(self):
        """Test complete user registration and profile setup"""
        # Register user
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify user and customer creation
        user = self.User.objects.get(username='newuser')
        customer = Customer.objects.get(user=user)
        self.assertEqual(customer.full_name, 'New User')
        
        # Login and access profile
        self.client.login(username='newuser', password='newpass123')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)

    def test_customer_address_management(self):
        """Test customer address creation and management"""
        # Create user and customer
        user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        customer = Customer.objects.create(user=user)
        
        # Create multiple addresses
        address1 = CustomerAddress.objects.create(
            customer=customer,
            type='billing',
            first_name='John',
            last_name='Doe',
            address_line_1='123 Main St',
            city='New York',
            country='USA',
            is_default=True
        )
        
        address2 = CustomerAddress.objects.create(
            customer=customer,
            type='shipping',
            first_name='John',
            last_name='Doe',
            address_line_1='456 Oak Ave',
            city='Los Angeles',
            country='USA'
        )
        
        # Test address relationships
        self.assertEqual(customer.addresses.count(), 2)
        self.assertEqual(address1.customer, customer)
        self.assertEqual(address2.customer, customer)
        self.assertTrue(address1.is_default)
        self.assertFalse(address2.is_default)