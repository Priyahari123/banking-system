from celery import shared_task
from django.db import transaction
from decimal import Decimal
from .models import BankAccount
import logging

logger = logging.getLogger(__name__)

@shared_task
def apply_interest_task(interest_percent):

    interest_percent = Decimal(str(interest_percent))

    logger.info(f"Starting apply_interest_task with interest_percent={interest_percent}")

    for account in BankAccount.objects.all():

        with transaction.atomic():

            old_balance = account.balance

            interest_amount = (old_balance * interest_percent) / Decimal('100')

            account.balance = old_balance + interest_amount

            account.save()

            logger.info(
                f"Account {account.user.customer_id} updated: {old_balance} -> {account.balance}"
            )

    logger.info("Interest applied to all accounts")




