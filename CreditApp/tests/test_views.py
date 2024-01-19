from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from CreditApp.models import Customer,Loan
from CreditApp.serializers import CustomerSerializer

class RegisterCustomerTest(TestCase):
    def setUp(self):
        self.client = APIClient()
    def test_register_customer_success(self):
        valid_data = {
            "monthly_income": 5000.0,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "age":20,
            "phone_number":8587976078
        }
        response = self.client.post(reverse('register-customer'), valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['approved_limit'], round(float(valid_data["monthly_income"]) * 36, -5))

    def test_register_customer_failure(self):
        invalid_data = {
            "monthly_income":"5000",
            "first_name": "John",
            "last_name": "Doe",
        }
        response = self.client.post(reverse('register-customer'), invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertIn("details", response.data)
        

class CheckEligibilityTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_check_eligibility_success(self):
        customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            age=30,
            phone_number="123456789",
            monthly_income=5000.0,
            approved_limit=50000 
        )
        loan = Loan.objects.create(
            customer=customer,
            loan_amount=20000,
            interest_rate=10,
            tenure=12,
            emis_paid_on_time=True,
            start_date="2024-01-01",
            end_date="2024-12-31"
        )

        valid_data = {
            'customer_id': customer.id,
            'loan_amount': 20000,
            'interest_rate': 10,
            'tenure': 12,
        }

        response = self.client.post(reverse('check-eligibility'), valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('customer_id', response.data)
        self.assertIn('approval', response.data)
        self.assertIn('interest_rate', response.data)
        self.assertIn('corrected_interest_rate', response.data)
        self.assertIn('tenure', response.data)
        self.assertIn('monthly_installment', response.data)

    def test_check_eligibility_failure_invalid_data(self):
        invalid_data = {
            'loan_amount': 20000,
            'interest_rate': 10,
            'tenure': 12,
        }

        response = self.client.post(reverse('check-eligibility'), invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        

class CreateLoanTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_loan_not_approved(self):
        customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            age=30,
            phone_number="1234567890",
            monthly_income=6000.0,
            approved_limit=180000.0
        )

        invalid_data = {
            "customer_id": customer.id,
            "loan_amount": 200000.0,
            "interest_rate": 5.0,
            "tenure": 12,
        }

        response = self.client.post(reverse('create-loan'), invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['loan_approved'])
        self.assertIsNone(response.data['loan_id'])

class ViewLoanTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_view_loan_success(self):
        customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            age=30,
            phone_number="1234567890",
            monthly_income=6000.0,
            approved_limit=180000.0
        )

        loan = Loan.objects.create(
            customer=customer,
            loan_amount=50000.0,
            interest_rate=10.0,
            tenure=12,
            monthly_payment=4500,
            emis_paid_on_time=6,
            start_date="2024-01-01",
            end_date="2024-12-31"
        )

        response = self.client.get(reverse('view-loan', args=[loan.id]), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['loan_id'], loan.id)
        self.assertEqual(response.data['customer']['id'], customer.id)

    def test_view_loan_not_found(self):
        response = self.client.get(reverse('view-loan', args=[999]), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)

class ViewLoansTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_view_loans_success(self):
        customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            age=30,
            phone_number="1234567890",
            monthly_income=6000.0,
            approved_limit=180000.0
        )

        loan1 = Loan.objects.create(
            customer=customer,
            loan_amount=50000.0,
            interest_rate=10.0,
            tenure=12,
            monthly_payment=4500,
            emis_paid_on_time=6,
            start_date="2024-01-01",
            end_date="2024-12-31"
        )

        loan2 = Loan.objects.create(
            customer=customer,
            loan_amount=30000.0,
            interest_rate=8.0,
            tenure=6,
            monthly_payment=5200,
            emis_paid_on_time=3,
            start_date="2024-02-01",
            end_date="2024-07-31"
        )

        response = self.client.get(reverse('view-loans', args=[customer.id]), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['loan_id'], loan1.id)
        self.assertEqual(response.data[1]['loan_id'], loan2.id)

    def test_view_loans_customer_not_found(self):
        response = self.client.get(reverse('view-loans', args=[999]), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('loan_id', response.data)  