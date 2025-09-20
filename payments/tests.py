from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.utils import timezone

from accounts.models import Customer
from orders.models import Order

from .models import Payment, PaymentAttempt


class PaymentModelTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.customer = Customer.objects.create(user=self.user)
        self.order = Order.objects.create(
            customer=self.customer,
            subtotal=Decimal("100.00"),
            total_amount=Decimal("100.00"),
        )

    def test_payment_creation(self):
        """Test creating a payment"""
        payment = Payment.objects.create(
            order=self.order,
            payment_method="paystack",
            status="pending",
            amount=Decimal("100.00"),
            currency="USD",
            paystack_reference="ref_123456",
            paystack_access_code="access_123456",
            paystack_transaction_id="txn_123456",
            gateway_response={"status": "success"},
            failure_reason=None,
        )

        self.assertEqual(payment.order, self.order)
        self.assertEqual(payment.payment_method, "paystack")
        self.assertEqual(payment.status, "pending")
        self.assertEqual(payment.amount, Decimal("100.00"))
        self.assertEqual(payment.currency, "USD")
        self.assertEqual(payment.paystack_reference, "ref_123456")
        self.assertEqual(payment.paystack_access_code, "access_123456")
        self.assertEqual(payment.paystack_transaction_id, "txn_123456")
        self.assertEqual(payment.gateway_response, {"status": "success"})
        self.assertIsNone(payment.failure_reason)
        self.assertIsNotNone(payment.created_at)
        self.assertIsNotNone(payment.updated_at)

    def test_payment_str_representation(self):
        """Test payment string representation"""
        payment = Payment.objects.create(
            order=self.order, amount=Decimal("100.00"), status="completed"
        )
        expected = f"Payment for Order {self.order.order_number} - Completed"
        self.assertEqual(str(payment), expected)

    def test_payment_is_successful_property(self):
        """Test payment is_successful property"""
        # Create separate orders for each payment
        order1 = Order.objects.create(
            customer=self.customer,
            subtotal=Decimal("100.00"),
            total_amount=Decimal("100.00"),
        )
        order2 = Order.objects.create(
            customer=self.customer,
            subtotal=Decimal("100.00"),
            total_amount=Decimal("100.00"),
        )

        # Successful payment
        successful_payment = Payment.objects.create(
            order=order1, amount=Decimal("100.00"), status="completed"
        )
        self.assertTrue(successful_payment.is_successful)

        # Failed payment
        failed_payment = Payment.objects.create(
            order=order2, amount=Decimal("100.00"), status="failed"
        )
        self.assertFalse(failed_payment.is_successful)

    def test_payment_is_pending_property(self):
        """Test payment is_pending property"""
        # Create separate orders for each payment
        order1 = Order.objects.create(
            customer=self.customer,
            subtotal=Decimal("100.00"),
            total_amount=Decimal("100.00"),
        )
        order2 = Order.objects.create(
            customer=self.customer,
            subtotal=Decimal("100.00"),
            total_amount=Decimal("100.00"),
        )
        order3 = Order.objects.create(
            customer=self.customer,
            subtotal=Decimal("100.00"),
            total_amount=Decimal("100.00"),
        )

        # Pending payment
        pending_payment = Payment.objects.create(
            order=order1, amount=Decimal("100.00"), status="pending"
        )
        self.assertTrue(pending_payment.is_pending)

        # Processing payment
        processing_payment = Payment.objects.create(
            order=order2, amount=Decimal("100.00"), status="processing"
        )
        self.assertTrue(processing_payment.is_pending)

        # Completed payment
        completed_payment = Payment.objects.create(
            order=order3, amount=Decimal("100.00"), status="completed"
        )
        self.assertFalse(completed_payment.is_pending)

    def test_payment_status_choices(self):
        """Test payment status choices"""
        statuses = [
            "pending",
            "processing",
            "completed",
            "failed",
            "cancelled",
            "refunded",
        ]
        for _i, status in enumerate(statuses):
            order = Order.objects.create(
                customer=self.customer,
                subtotal=Decimal("100.00"),
                total_amount=Decimal("100.00"),
            )
            payment = Payment.objects.create(
                order=order, amount=Decimal("100.00"), status=status
            )
            self.assertEqual(payment.status, status)

    def test_payment_method_choices(self):
        """Test payment method choices"""
        methods = ["paystack", "bank_transfer", "cash_on_delivery"]
        for method in methods:
            order = Order.objects.create(
                customer=self.customer,
                subtotal=Decimal("100.00"),
                total_amount=Decimal("100.00"),
            )
            payment = Payment.objects.create(
                order=order, payment_method=method, amount=Decimal("100.00")
            )
            self.assertEqual(payment.payment_method, method)

    def test_payment_ordering(self):
        """Test payment ordering by created_at (newest first)"""
        order1 = Order.objects.create(
            customer=self.customer,
            subtotal=Decimal("100.00"),
            total_amount=Decimal("100.00"),
        )
        order2 = Order.objects.create(
            customer=self.customer,
            subtotal=Decimal("200.00"),
            total_amount=Decimal("200.00"),
        )

        payment1 = Payment.objects.create(order=order1, amount=Decimal("100.00"))

        payment2 = Payment.objects.create(order=order2, amount=Decimal("200.00"))

        payments = Payment.objects.all()
        self.assertEqual(payments[0], payment2)  # Newest first
        self.assertEqual(payments[1], payment1)


class PaymentAttemptModelTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.customer = Customer.objects.create(user=self.user)
        self.order = Order.objects.create(
            customer=self.customer,
            subtotal=Decimal("100.00"),
            total_amount=Decimal("100.00"),
        )
        self.payment = Payment.objects.create(
            order=self.order, amount=Decimal("100.00")
        )

    def test_payment_attempt_creation(self):
        """Test creating a payment attempt"""
        attempt = PaymentAttempt.objects.create(
            payment=self.payment,
            paystack_reference="ref_123456",
            status="success",
            gateway_response={"status": "success", "message": "Payment successful"},
        )

        self.assertEqual(attempt.payment, self.payment)
        self.assertEqual(attempt.paystack_reference, "ref_123456")
        self.assertEqual(attempt.status, "success")
        self.assertEqual(
            attempt.gateway_response,
            {"status": "success", "message": "Payment successful"},
        )
        self.assertIsNotNone(attempt.created_at)
        self.assertIsNotNone(attempt.updated_at)

    def test_payment_attempt_str_representation(self):
        """Test payment attempt string representation"""
        attempt = PaymentAttempt.objects.create(
            payment=self.payment, paystack_reference="ref_123456", status="failed"
        )
        expected = f"Payment attempt for {self.order.order_number} - failed"
        self.assertEqual(str(attempt), expected)

    def test_payment_attempt_ordering(self):
        """Test payment attempt ordering by created_at (newest first)"""
        attempt1 = PaymentAttempt.objects.create(
            payment=self.payment, paystack_reference="ref_111111", status="failed"
        )

        attempt2 = PaymentAttempt.objects.create(
            payment=self.payment, paystack_reference="ref_222222", status="success"
        )

        attempts = PaymentAttempt.objects.all()
        self.assertEqual(attempts[0], attempt2)  # Newest first
        self.assertEqual(attempts[1], attempt1)


class PaymentViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.customer = Customer.objects.create(user=self.user)
        self.order = Order.objects.create(
            customer=self.customer,
            subtotal=Decimal("100.00"),
            total_amount=Decimal("100.00"),
        )
        self.payment = Payment.objects.create(
            order=self.order, amount=Decimal("100.00")
        )

    def test_payment_views_authenticated(self):
        """Test payment views for authenticated user"""
        self.client.login(username="testuser", password="testpass123")

        # Test payment list view (if exists)
        # response = self.client.get(reverse('payments:payment_list'))
        # self.assertEqual(response.status_code, 200)

        # Test payment detail view (if exists)
        # response = self.client.get(reverse('payments:payment_detail', args=[self.payment.id]))
        # self.assertEqual(response.status_code, 200)

    def test_payment_views_unauthenticated(self):
        """Test payment views for unauthenticated user"""
        # Test payment list view (if exists)
        # response = self.client.get(reverse('payments:payment_list'))
        # self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test payment detail view (if exists)
        # response = self.client.get(reverse('payments:payment_detail', args=[self.payment.id]))
        # self.assertEqual(response.status_code, 302)  # Redirect to login


class PaymentIntegrationTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.customer = Customer.objects.create(user=self.user)
        self.order = Order.objects.create(
            customer=self.customer,
            subtotal=Decimal("100.00"),
            total_amount=Decimal("100.00"),
        )

    def test_payment_order_relationship(self):
        """Test payment-order relationship"""
        payment = Payment.objects.create(
            order=self.order, amount=Decimal("100.00"), status="completed"
        )

        # Test order payment relationship
        self.assertEqual(self.order.payment, payment)
        self.assertEqual(payment.order, self.order)

    def test_payment_attempt_payment_relationship(self):
        """Test payment attempt-payment relationship"""
        payment = Payment.objects.create(order=self.order, amount=Decimal("100.00"))

        attempt1 = PaymentAttempt.objects.create(
            payment=payment, paystack_reference="ref_111111", status="failed"
        )

        attempt2 = PaymentAttempt.objects.create(
            payment=payment, paystack_reference="ref_222222", status="success"
        )

        # Test payment attempts relationship
        self.assertEqual(payment.attempts.count(), 2)
        self.assertIn(attempt1, payment.attempts.all())
        self.assertIn(attempt2, payment.attempts.all())

    def test_complete_payment_flow(self):
        """Test complete payment flow"""
        # Create payment
        payment = Payment.objects.create(
            order=self.order,
            payment_method="paystack",
            amount=Decimal("100.00"),
            status="pending",
        )

        # # Create failed attempt
        # failed_attempt = PaymentAttempt.objects.create(
        #     payment=payment,
        #     paystack_reference="ref_failed",
        #     status="failed",
        #     gateway_response={"error": "Insufficient funds"},
        # )

        # # Create successful attempt
        # successful_attempt = PaymentAttempt.objects.create(
        #     payment=payment,
        #     paystack_reference="ref_success",
        #     status="success",
        #     gateway_response={"status": "success", "transaction_id": "txn_123"},
        # )

        # Update payment status
        payment.status = "completed"
        payment.paystack_transaction_id = "txn_123"
        payment.paid_at = timezone.now()
        payment.save()

        # Verify final state
        self.assertEqual(payment.status, "completed")
        self.assertTrue(payment.is_successful)
        self.assertFalse(payment.is_pending)
        self.assertEqual(payment.attempts.count(), 2)
        self.assertIsNotNone(payment.paid_at)
