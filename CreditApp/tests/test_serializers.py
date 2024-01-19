from django.test import TestCase
from CreditApp.models import Customer, Loan
from CreditApp.serializers import CustomerSerializer, LoanSerializer

class CustomerSerializerTest(TestCase):
    def test_valid_customer_serialization(self):
        # Ensure that the serializer properly serializes valid customer data
        valid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "age": 30,
            "phone_number": "1234567890",
            "monthly_income": 5000.0,
            "approved_limit": 10000.0,
        }
        serializer = CustomerSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_customer_serialization(self):
        # Ensure that the serializer handles invalid customer data
        invalid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "age": -30,
            "phone_number": "1234567890",
            "monthly_income": 5000.0,
            "approved_limit": 10000.0,
        }
        serializer = CustomerSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

class LoanSerializerTest(TestCase):

    def test_invalid_loan_serialization(self):
        # Ensure that the serializer handles invalid loan data
        invalid_data = {
            "customer": 1,  # Non-existent customer ID
            "loan_amount": 5000.0,
            "tenure": 12,
            "interest_rate": 10.0,
            "monthly_payment": 450.0,
            "emis_paid_on_time": 6,
            "start_date": "2023-01-01",
            "end_date": "2022-12-31",  # Invalid end date
        }
        serializer = LoanSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('customer', serializer.errors)
        self.assertIn('end_date', serializer.errors)
