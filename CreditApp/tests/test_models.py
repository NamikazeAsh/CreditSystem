from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from CreditApp.models import Customer, Loan

class CustomerModelTest(TestCase):
    def test_customer_creation(self):
        customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            age=30,
            phone_number="1234567890",
            monthly_income=5000.0,
            approved_limit=10000.0
        )

        self.assertEqual(customer.first_name, "John")
        self.assertEqual(customer.last_name, "Doe")
        self.assertEqual(customer.age, 30)
        self.assertEqual(customer.phone_number, "1234567890")
        self.assertEqual(customer.monthly_income, 5000.0)
        self.assertEqual(customer.approved_limit, 10000.0)

    def test_customer_creation_invalid_data(self):
        with self.assertRaises(ValidationError):
            customer = Customer(
                first_name="John",
                last_name="Doe",
                age=-30,
                phone_number="1234567890",
                monthly_income=5000.0,
                approved_limit=10000.0
            )

            customer.full_clean()

class LoanModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            age=30,
            phone_number="1234567890",
            monthly_income=5000.0,
            approved_limit=10000.0
        )

    def test_loan_creation(self):
        loan = Loan(
            customer=self.customer,
            loan_amount=5000.0,
            tenure=12,
            interest_rate=10.0,
            monthly_payment=500.0,
            emis_paid_on_time=6,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365)
        )

        loan.full_clean()

        loan.save()

        self.assertEqual(loan.customer, self.customer)
        self.assertEqual(loan.loan_amount, 5000.0)
        self.assertEqual(loan.tenure, 12)
        self.assertEqual(loan.interest_rate, 10.0)
        self.assertEqual(loan.monthly_payment, 500.0)
        self.assertEqual(loan.emis_paid_on_time, 6)
        self.assertEqual(loan.start_date, timezone.now().date())
        self.assertEqual(loan.end_date, timezone.now().date() + timezone.timedelta(days=365))

    def test_loan_creation_invalid_data(self):
        with self.assertRaises(ValidationError):
            loan = Loan(
                customer=self.customer,
                loan_amount=5000.0,
                tenure=12,
                interest_rate=10.0,
                monthly_payment=500.0,
                emis_paid_on_time=6,
                start_date=timezone.now().date() - timezone.timedelta(days=7),
                end_date=timezone.now().date() + timezone.timedelta(days=365)
            )
            loan.full_clean()