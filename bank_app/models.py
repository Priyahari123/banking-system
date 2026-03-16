from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import random

class CustomUserManager(BaseUserManager):
    def create_user(self, email, mobile_number, role, password=None,customer_id=None):
        if not email:
            raise ValueError('Email required')
        email = self.normalize_email(email)
        user = self.model(email=email, mobile_number=mobile_number, role=role, customer_id=customer_id)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, mobile_number, password=None):
        customer_id = f"MGR{random.randint(1000,9999)}"
   
        user = self.create_user(email, mobile_number, role='manager', password=password, customer_id=customer_id)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('customer','Customer'),
        ('employee','Employee'),
        ('manager','Manager')
    ]
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15)
    customer_id = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['mobile_number']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"



class BankAccount(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.customer_id} - {self.balance}"



class Loan(models.Model):
    STATUS_CHOICES = [('pending','Pending'), ('completed','Completed')]
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    total_amount = models.FloatField()
    amount_paid = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Loan {self.id} - {self.account.user.customer_id}"