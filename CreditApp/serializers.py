from rest_framework import serializers
from .models import Customer, Loan

class CustomerSerializer(serializers.ModelSerializer):
    
    def validate(self, attrs):
        attrs = super().validate(attrs)
        age = attrs.get('age')
        if age is not None and age < 0:
            raise serializers.ValidationError("Age must be a non-negative value.")
        return attrs
    
    class Meta:
        model = Customer
        fields = '__all__'

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'