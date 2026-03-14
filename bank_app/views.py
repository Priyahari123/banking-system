from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import BankAccount, CustomUser
from .serializers import BankAccountSerializer, LoanCreateSerializer
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
from .task import apply_interest_task


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

        # Dynamically calculate updated balance
        total_loans = sum(loan.total_amount for loan in Loan.objects.filter(account=account))
        total_paid = sum(loan.amount_paid for loan in Loan.objects.filter(account=account))
        account.balance = total_loans - total_paid
        account.save()
        
        return account

    def get(self, request, *args, **kwargs):
        account = self.get_object()
        if not account:
            return Response({"detail":"Access denied"}, status=403)

        serializer = self.get_serializer(account)
        data = serializer.data

        # Include detailed loan info
        loans = Loan.objects.filter(account=account)
        data['loans'] = [
            {
                "id": loan.id,
                "total_amount": loan.total_amount,
                "amount_paid": loan.amount_paid,
                "status": loan.status
            }
            for loan in loans
        ]
        return Response(data)


class CreateLoanAPIView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        serializer = LoanCreateSerializer(data=request.data)
        if serializer.is_valid():
            loan = serializer.save()
            return Response({
                "loan_id": loan.id,
                "customer_id": loan.account.user.customer_id,
                "total_amount": loan.total_amount,
                "status": loan.status,
                "updated_balance": loan.account.balance
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=400)

class PayLoanAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        customer_id = request.data.get('customer_id')
        loan_id = request.data.get('loan_id')  # Specify which loan to pay
        amount = float(request.data.get('amount', 0))
        user = request.user

        if amount <= 0:
            return Response({"detail": "Invalid amount"}, status=400)

        # Customer can pay only their loan
        if user.role == 'customer' and user.customer_id != customer_id:
            return Response({"detail": "Access denied"}, status=403)

        try:
            account = BankAccount.objects.get(user__customer_id=customer_id)
        except BankAccount.DoesNotExist:
            return Response({"detail": "Account not found"}, status=404)

        # Filter the specific loan
        try:
            loan = Loan.objects.get(account=account, id=loan_id, status='pending')
        except Loan.DoesNotExist:
            return Response({"detail": "No active loan with this ID"}, status=400)

        if amount > (loan.total_amount - loan.amount_paid):
            return Response({"detail": "Overpayment not allowed"}, status=400)

        # Update loan payment
        loan.amount_paid += amount
        if loan.amount_paid >= loan.total_amount:
            loan.status = 'completed'
        loan.save()

        # Recalculate the account balance dynamically
        total_loans = sum(l.total_amount for l in Loan.objects.filter(account=account))
        total_paid = sum(l.amount_paid for l in Loan.objects.filter(account=account))
        account.balance = total_loans - total_paid
        account.save()

        return Response({
            "loan_id": loan.id,
            "paid_amount": loan.amount_paid,
            "pending_amount": loan.total_amount - loan.amount_paid,
            "updated_balance": account.balance
        })
    


class ApplyInterestAPIView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        interest_percent = request.data.get('interest_percent')
        if interest_percent is None:
            return Response({"detail": "interest_percent is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            interest_percent = float(interest_percent)
            if interest_percent <= 0:
                return Response({"detail": "interest_percent must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"detail": "interest_percent must be a number"}, status=status.HTTP_400_BAD_REQUEST)

        # Trigger Celery task
        apply_interest_task.delay(interest_percent)

        return Response({"detail": f"Interest of {interest_percent}% applied asynchronously."}, status=status.HTTP_200_OK)

class CreateUserAPIView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [IsAuthenticated, IsManager]
