from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer,Loan
from .serializers import CustomerSerializer,LoanSerializer


@api_view(['POST'])
def register_customer(request):
    data = request.data
    data['approved_limit'] = round(float(data["monthly_income"]) * 36, -5)
    serializer = CustomerSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response({
            "error": "Registration failed",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def check_eligibility(request):
    try:
        customer_id = request.data['customer_id']
        loan_amount = request.data['loan_amount']
        interest_rate = request.data['interest_rate']
        tenure = request.data['tenure']

        # Get customer details
        customer = get_object_or_404(Customer, pk=customer_id)

        # Check past loans paid on time
        past_loans_paid_on_time = Loan.objects.filter(customer=customer, emis_paid_on_time=True).count()

        # Check number of loans taken in the past
        number_of_loans_taken = Loan.objects.filter(customer=customer).count()

        # Check loan activity in the current year
        loan_activity_current_year = Loan.objects.filter(customer=customer, start_date__year=2024).count()

        # Check loan approved volume and sum of current loans
        loan_approved_volume = sum(loan.loan_amount for loan in Loan.objects.filter(customer=customer))
        current_loans_amount = sum(loan.loan_amount for loan in Loan.objects.filter(customer=customer))
        approved_limit = customer.approved_limit

        # Calculate credit score based on provided criteria
        weight_past_loans_paid_on_time = 0.3
        weight_number_of_loans_taken = 0.2
        weight_loan_activity_current_year = 0.2
        weight_loan_approved_volume = 0.3
        credit_score = (
            weight_past_loans_paid_on_time * past_loans_paid_on_time +
            weight_number_of_loans_taken * number_of_loans_taken +
            weight_loan_activity_current_year * loan_activity_current_year +
            weight_loan_approved_volume * (loan_approved_volume / approved_limit)) * 100
        print("CREDIT SCORE ", credit_score)

        if current_loans_amount > approved_limit:
            credit_score = 0

        if credit_score > 50:
            approval = True
        elif 30 < credit_score <= 50:
            approval = interest_rate > 12
        elif 10 < credit_score <= 30:
            approval = interest_rate > 16
        else:
            approval = False

        total_emis = sum(loan.monthly_payment or 0 for loan in Loan.objects.filter(customer=customer))
        if total_emis > 0.5 * customer.monthly_income:
            approval = False

        corrected_interest_rate = (
            12 if approval and interest_rate < 12 else
            16 if approval and interest_rate > 16 else
            interest_rate
        )

        monthly_installment = round((loan_amount * corrected_interest_rate / 1200) / (1 - (1 + corrected_interest_rate / 1200) ** (-tenure)), 2)

        response_data = {
            'customer_id': customer_id,
            'approval': approval,
            'interest_rate': interest_rate,
            'corrected_interest_rate': corrected_interest_rate,
            'tenure': tenure,
            'monthly_installment': monthly_installment,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except KeyError:
        return Response({'error': 'Invalid request data'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_loan(request):
    try:
        customer_id = request.data['customer_id']
        loan_amount = request.data['loan_amount']
        interest_rate = request.data['interest_rate']
        tenure = request.data['tenure']

        customer = get_object_or_404(Customer, pk=customer_id)
        
        eligibility_response = check_eligibility_internal(customer_id, loan_amount, interest_rate, tenure)

        if eligibility_response['approval']:
            loan = Loan.objects.create(
                customer=customer,
                loan_amount=loan_amount,
                interest_rate=interest_rate,
                tenure=tenure,
                emis_paid_on_time=True,
                start_date="2024-01-01",
                end_date="2024-12-31",
                monthly_payment = eligibility_response['monthly_installment']
            )

            response_data = {
                'loan_id': loan.id,
                'customer_id': customer_id,
                'loan_approved': True,
                'message': 'Loan approved. Monthly installment details below.',
                'monthly_installment': eligibility_response['monthly_installment'],
            }
        else:
            response_data = {
                'loan_id': None,
                'customer_id': customer_id,
                'loan_approved': False,
                'message': 'Loan not approved. Eligibility criteria not met.',
                'monthly_installment': 0,
            }

        return Response(response_data, status=status.HTTP_200_OK)

    except KeyError:
        return Response({'error': 'Invalid request data'}, status=status.HTTP_400_BAD_REQUEST)

# Helper function for internal use to check eligibility
def check_eligibility_internal(customer_id, loan_amount, interest_rate, tenure):

    customer = get_object_or_404(Customer, pk=customer_id)

    past_loans_paid_on_time = Loan.objects.filter(customer=customer, emis_paid_on_time=True).count()
    number_of_loans_taken = Loan.objects.filter(customer=customer).count()
    loan_activity_current_year = Loan.objects.filter(customer=customer, start_date__year=2024).count()
    loan_approved_volume = sum(loan.loan_amount for loan in Loan.objects.filter(customer=customer))
    current_loans_amount = sum(loan.loan_amount for loan in Loan.objects.filter(customer=customer))
    approved_limit = customer.approved_limit

    # Calculate credit score based on provided criteria
    weight_past_loans_paid_on_time = 0.3
    weight_number_of_loans_taken = 0.2
    weight_loan_activity_current_year = 0.2
    weight_loan_approved_volume = 0.3
    credit_score = (
        weight_past_loans_paid_on_time * past_loans_paid_on_time +
        weight_number_of_loans_taken * number_of_loans_taken +
        weight_loan_activity_current_year * loan_activity_current_year +
        weight_loan_approved_volume * (loan_approved_volume / approved_limit)) * 100
    print("CREDIT SCORE ", credit_score)

    if current_loans_amount > approved_limit:
            credit_score = 0

    if credit_score > 50:
        approval = True
    elif 30 < credit_score <= 50:
        approval = interest_rate > 12
    elif 10 < credit_score <= 30:
        approval = interest_rate > 16
    else:
        approval = False

    total_emis = sum(loan.monthly_payment or 0 for loan in Loan.objects.filter(customer=customer))
    if total_emis > 0.5 * customer.monthly_income:
        approval = False

    # Correct the interest rate if it doesn't match the credit limit
    corrected_interest_rate = (
        12 if approval and interest_rate < 12 else
        16 if approval and interest_rate > 16 else
        interest_rate
    )

    monthly_installment = round((loan_amount * corrected_interest_rate / 1200) / (1 - (1 + corrected_interest_rate / 1200) ** (-tenure)), 2)

    return {
        'customer_id': customer_id,
        'approval': approval,
        'interest_rate': interest_rate,
        'corrected_interest_rate': corrected_interest_rate,
        'tenure': tenure,
        'monthly_installment': monthly_installment,
    }
    
    
@api_view(['GET'])
def view_loan(request, loan_id):
    try:
        loan = get_object_or_404(Loan, pk=loan_id)
        customer = loan.customer

        customer_data = CustomerSerializer(customer).data
        loan_data = LoanSerializer(loan).data

        response_data = {
            'loan_id': loan_data['id'],
            'customer': customer_data,
            'loan_amount': loan_data['loan_amount'],
            'interest_rate': loan_data['interest_rate'],
            'monthly_installment': loan_data['monthly_payment'],
            'tenure': loan_data['tenure'],
        }

        return Response(response_data, status=200)

    except Loan.DoesNotExist:
        return Response({'error': 'Loan not found'}, status=404)
    

@api_view(['GET'])
def view_loans(request, customer_id):
    try:
        loans = Loan.objects.filter(customer__id=customer_id)
        loans_data = []

        for loan in loans:
            loan_data = LoanSerializer(loan).data
            repayments_left = loan.tenure - loan.emis_paid_on_time
            loan_item = {
                'loan_id': loan_data['id'],
                'loan_amount': loan_data['loan_amount'],
                'interest_rate': loan_data['interest_rate'],
                'monthly_installment': loan_data['monthly_payment'],
                'repayments_left': repayments_left,
            }
            loans_data.append(loan_item)

        return Response(loans_data, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=400)

