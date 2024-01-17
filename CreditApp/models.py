from django.db import models

class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField()
    phone_number = models.CharField(max_length=15)
    monthly_income = models.FloatField(null = True)
    approved_limit = models.FloatField(null=True)

class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_amount = models.FloatField(null = True)
    tenure = models.IntegerField(null = True)
    interest_rate = models.FloatField(null = True)
    monthly_payment = models.IntegerField(null = True)
    emis_paid_on_time = models.IntegerField(default=0,null = True)
    start_date = models.DateField(null = True)
    end_date = models.DateField(null = True)

