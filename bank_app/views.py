from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import BankAccount, CustomUser
from .serializers import BankAccountSerializer
from rest_framework.views import APIView
from .models import Loan
from celery import shared_task
from rest_framework import generics
from .serializers import UserCreateSerializer
from .permissions import IsManager
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework import status


class LoginAPIView(APIView):
    permission_classes = []  # anyone can login

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"detail":"Email and password required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(email=email, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user_id": user.id,
                "role": user.role,
                "customer_id": user.customer_id
            })
        else:
            return Response({"detail":"Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)



class AccountDetailAPIView(generics.RetrieveAPIView):
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        customer_id = self.kwargs['customer_id']
        user = self.request.user
        try:
            account = BankAccount.objects.get(user__customer_id=customer_id)
        except BankAccount.DoesNotExist:
            return None

        # Role-based access
        if user.role == 'customer' and user.customer_id != customer_id:
            return None
        if user.role == 'employee' and account.user.role != 'customer':
            return None
        return account

    def get(self, request, *args, **kwargs):
        account = self.get_object()
        if not account:
            return Response({"detail":"Access denied"}, status=403)
        serializer = self.get_serializer(account)
        return Response(serializer.data)
    
class PayLoanAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        customer_id = request.data.get('customer_id')
        amount = float(request.data.get('amount',0))
        user = request.user

        if amount <= 0:
            return Response({"detail":"Invalid amount"}, status=400)

        # Customer can pay only their loan
        if user.role == 'customer' and user.customer_id != customer_id:
            return Response({"detail":"Access denied"}, status=403)

        try:
            account = BankAccount.objects.get(user__customer_id=customer_id)
            loan = Loan.objects.filter(account=account, status='pending').first()
            if not loan:
                return Response({"detail":"No active loan"}, status=400)
        except BankAccount.DoesNotExist:
            return Response({"detail":"Account not found"}, status=404)

        if amount > (loan.total_amount - loan.amount_paid):
            return Response({"detail":"Overpayment not allowed"}, status=400)

        loan.amount_paid += amount
        if loan.amount_paid >= loan.total_amount:
            loan.status = 'completed'
        loan.save()

        return Response({"loan_id": loan.id, "pending_amount": loan.total_amount - loan.amount_paid})
    
@shared_task
def apply_interest_task(interest_percent):
    updated_accounts = []
    for account in BankAccount.objects.all():
        account.balance += account.balance * interest_percent / 100
        account.save()
        updated_accounts.append({"customer_id": account.user.customer_id, "new_balance": account.balance})
    return updated_accounts

class ApplyInterestAPIView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        percent = float(request.data.get('interest_percent',0))
        task = apply_interest_task.delay(percent)
        return Response({"detail":"Interest application started asynchronously"})
    

class CreateUserAPIView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [IsAuthenticated, IsManager]
