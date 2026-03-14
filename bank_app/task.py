from celery import shared_task
from django.db import transaction
from .models import BankAccount
import logging

logger = logging.getLogger(__name__)

@shared_task
def apply_interest_task(interest_percent):
    logger.info(f"Starting apply_interest_task with interest_percent={interest_percent}")
    updated_accounts = []

    for account in BankAccount.objects.all():
        with transaction.atomic():
            old_balance = account.balance
            account.balance += account.balance * interest_percent / 100
            account.save()

            updated_accounts.append({
                "customer_id": account.user.customer_id,
                "old_balance": float(old_balance),
                "new_balance": float(account.balance)
            })

            logger.info(f"Account {account.user.customer_id} updated: {old_balance} -> {account.balance}")

    logger.info(f"Task completed. {len(updated_accounts)} accounts updated.")
    return updated_accounts




