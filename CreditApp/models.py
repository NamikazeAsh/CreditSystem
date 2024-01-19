from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

def validate_date_not_past(value):
    if value < timezone.now().date():
        raise ValidationError("Date cannot be in the past.")

class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField()
    phone_number = models.CharField(max_length=15)
    monthly_income = models.FloatField(null = True)
    approved_limit = models.FloatField(null=True)
    
    def clean(self):
        if self.age<0:
            raise ValidationError("Age cannot be below 0")

class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_amount = models.FloatField(null = True)
    tenure = models.IntegerField(null = True)
    interest_rate = models.FloatField(null = True)
    monthly_payment = models.IntegerField(null = True)
    emis_paid_on_time = models.IntegerField(default=0,null = True)
    start_date = models.DateField(null=True, validators=[validate_date_not_past])
    end_date = models.DateField(null=True, validators=[validate_date_not_past])
    
    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Start date cannot be after end date.")

