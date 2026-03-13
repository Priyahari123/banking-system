from rest_framework import serializers
from .models import CustomUser, BankAccount, Loan

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