from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer,Loan
from .serializers import CustomerSerializer,LoanSerializer


@api_view(['POST'])
def register_customer(request):
    data= request.data
    data['approved_limit'] = round(float(data["monthly_income"]) * 36, -5)
    serializer = CustomerSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        credit_score = (
            past_loans_paid_on_time * 10 +
            number_of_loans_taken * 5 +
            loan_activity_current_year * 7 +
            (loan_approved_volume / approved_limit) * 20
        )
        print("CREDIT SCORE ", credit_score)

        # If sum of current loans > approved limit, set credit score to 0
        if current_loans_amount > approved_limit:
            credit_score = 0

        # Check loan eligibility based on credit score
        if credit_score > 50:
            approval = True
        elif 30 < credit_score <= 50:
            approval = interest_rate > 12
        elif 10 < credit_score <= 30:
            approval = interest_rate > 16
        else:
            approval = False

        # Check if sum of all current EMIs > 50% of monthly salary
        total_emis = sum(loan.monthly_payment or 0 for loan in Loan.objects.filter(customer=customer))
        if total_emis > 0.5 * customer.monthly_income:
            approval = False

        # Correct the interest rate if it doesn't match the credit limit
        corrected_interest_rate = (
            12 if approval and interest_rate < 12 else
            16 if approval and interest_rate > 16 else
            interest_rate
        )

        # Calculate monthly installment inline
        monthly_installment = round((loan_amount * corrected_interest_rate / 1200) / (1 - (1 + corrected_interest_rate / 1200) ** (-tenure)), 2)

        # Respond with eligibility information
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

        # Sample logic:
        eligibility_score = calculate_eligibility_score(customer_id, loan_amount, interest_rate, tenure)

        if eligibility_score > 50:
            Loan.objects.create(
                customer_id=customer_id,
                loan_amount=loan_amount,
                interest_rate=interest_rate,
                tenure=tenure,
                monthly_payment= (loan_amount * interest_rate / 1200) / (1 - (1 + interest_rate / 1200) ** (-tenure))
                # Add other fields as needed
            )
            response_data = {'message': 'Loan created successfully'}
        else:
            response_data = {'error': 'Customer is not eligible for the loan'}

        return Response(response_data, status=status.HTTP_200_OK)

    except KeyError:
        return Response({'error': 'Invalid request data'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def view_loan(request, loan_id):
    try:
        loan = get_object_or_404(Loan, pk=loan_id)
        # Implement your logic to serialize the loan object
        serializer = LoanSerializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Loan.DoesNotExist:
        return Response({'error': 'Loan does not exist'}, status=status.HTTP_404_NOT_FOUND)

