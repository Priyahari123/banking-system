from rest_framework import serializers
from .models import CustomUser, BankAccount, Loan
import re

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['id','total_amount','amount_paid','status']

class BankAccountSerializer(serializers.ModelSerializer):
    loans = LoanSerializer(source='loan_set', many=True)
    name = serializers.CharField(source='user.email', read_only=True)
    customer_id = serializers.CharField(source='user.customer_id', read_only=True)

    class Meta:
        model = BankAccount
        fields = ['customer_id','name','balance','loans']

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email','mobile_number','role','customer_id','password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        # create bank account
        from .models import BankAccount
        BankAccount.objects.create(user=user)
        return user




class LoanCreateSerializer(serializers.ModelSerializer):
    customer_id = serializers.CharField(write_only=True)

    class Meta:
        model = Loan
        fields = ['customer_id', 'total_amount']

    def validate_customer_id(self, value):
        """
        Ensure customer_id contains letters + numbers
        Example: CUST1001
        """
        if not re.match(r'^[A-Za-z]+\d+$', value):
            raise serializers.ValidationError(
                "customer_id must contain letters followed by numbers, e.g., CUST1001"
            )
        return value

    def create(self, validated_data):
        customer_id = validated_data.pop('customer_id')
        try:
            account = BankAccount.objects.get(user__customer_id=customer_id)
        except BankAccount.DoesNotExist:
            raise serializers.ValidationError("Customer account not found.")

        loan = Loan.objects.create(account=account, **validated_data)

        # Update customer balance (total loans - total paid)
        total_loans = sum(l.total_amount for l in Loan.objects.filter(account=account))
        total_paid = sum(l.amount_paid for l in Loan.objects.filter(account=account))
        account.balance = total_loans - total_paid
        account.save()

        return loan