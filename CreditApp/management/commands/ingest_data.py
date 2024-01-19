import os
from django.core.management.base import BaseCommand
import pandas as pd
from CreditApp.models import Loan,Customer

class Command(BaseCommand):
    help = 'Ingest data from Excel sheets'

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        customer_data = pd.read_excel(os.path.join(base_dir, 'customer_data.xlsx'))
        loan_data = pd.read_excel(os.path.join(base_dir, 'loan_data.xlsx'))
        
        for _, customer_row in customer_data.iterrows():
            Customer.objects.create(
                id = customer_row['Customer ID'],
                first_name=customer_row['First Name'],
                last_name=customer_row['Last Name'],
                age=customer_row['Age'],
                monthly_income=customer_row['Monthly Salary'],
                phone_number=customer_row['Phone Number'],
                approved_limit=36 * customer_row['Approved Limit'], #based on requirement
            )

        for _, loan_row in loan_data.iterrows():
            customer = Customer.objects.get(pk=loan_row['Customer ID'])
            Loan.objects.create(
                customer=customer,
                loan_amount=loan_row['Loan Amount'],
                interest_rate=loan_row['Interest Rate'],
                tenure=loan_row['Tenure'],
                emis_paid_on_time=loan_row['EMIs paid on Time'],
                start_date=loan_row['Date of Approval'],
                end_date=loan_row['End Date']
            )
