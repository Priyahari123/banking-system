from celery import shared_task
from .models import BankAccount

@shared_task
def apply_interest_task(interest_percent):
    updated_accounts = []
    for account in BankAccount.objects.all():
        account.balance += account.balance * interest_percent / 100
        account.save()
        updated_accounts.append({
            "customer_id": account.user.customer_id,
            "new_balance": account.balance
        })
    return updated_accounts