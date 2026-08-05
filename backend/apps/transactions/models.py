import uuid
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator


class NetworkChoices(models.TextChoices):
    BEP20 = 'BEP20', _('BEP20 (BSC)')
    TRC20 = 'TRC20', _('TRC20 (TRON)')


class Deposit(models.Model):
    """
    User deposit (fiat or crypto proof-of-payment).

    Flow: User uploads proof → PENDING → Admin reviews → APPROVED (wallet credited) / REJECTED.
    Approved deposits trigger a WalletTransaction + update total_deposited on the Wallet.
    All approval logic must run inside a database transaction.
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='deposits',
        verbose_name=_('User'),
    )

    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('Amount ($)'),
    )
    network = models.CharField(
        max_length=10,
        choices=NetworkChoices.choices,
        verbose_name=_('Network'),
    )
    sender_wallet_address = models.CharField(
        max_length=200, blank=True, verbose_name=_('Sender Wallet Address')
    )
    txn_hash = models.CharField(
        max_length=200, blank=True, db_index=True, verbose_name=_('Transaction Hash')
    )
    payment_proof = models.FileField(
        upload_to='deposits/', blank=True, null=True, verbose_name=_('Payment Proof')
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name=_('Status'),
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_deposits',
        verbose_name=_('Reviewed By'),
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Reviewed At'))
    notes = models.TextField(blank=True, verbose_name=_('Admin Notes'))

    class Meta:
        verbose_name = _('Deposit')
        verbose_name_plural = _('Deposits')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self) -> str:
        return f"Deposit ${self.amount} by {self.user} [{self.status}]"


class Withdrawal(models.Model):
    """
    User withdrawal request.

    Two types per SRS:
    - PROFIT: minimum $10, fee $1 per transaction.
    - CAPITAL: minimum $100, fund-management charge $10.

    Admin approves/rejects. Approval debits wallet balance atomically.
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')
        PROCESSING = 'PROCESSING', _('Processing')

    class WithdrawalType(models.TextChoices):
        PROFIT = 'PROFIT', _('Profit Withdrawal')
        CAPITAL = 'CAPITAL', _('Capital Withdrawal')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='withdrawals',
        verbose_name=_('User'),
    )

    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('Requested Amount ($)'),
    )
    withdrawal_type = models.CharField(
        max_length=10,
        choices=WithdrawalType.choices,
        default=WithdrawalType.PROFIT,
        db_index=True,
        verbose_name=_('Withdrawal Type'),
    )
    fee = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('1.00'),
        verbose_name=_('Transaction Fee ($)'),
        help_text=_('$1 per withdrawal per SRS'),
    )
    capital_charge = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Capital Withdrawal Charge ($)'),
        help_text=_('$10 fund-management charge for capital withdrawals'),
    )
    net_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name=_('Net Amount ($)'),
        help_text=_('amount - fee - capital_charge'),
    )
    network = models.CharField(
        max_length=10,
        choices=NetworkChoices.choices,
        verbose_name=_('Network'),
    )
    wallet_address = models.CharField(
        max_length=200, verbose_name=_('Destination Wallet Address')
    )
    txn_hash = models.CharField(
        max_length=200, blank=True, db_index=True, verbose_name=_('Transaction Hash')
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name=_('Status'),
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_withdrawals',
        verbose_name=_('Reviewed By'),
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Reviewed At'))
    notes = models.TextField(blank=True, verbose_name=_('Admin Notes'))

    class Meta:
        verbose_name = _('Withdrawal')
        verbose_name_plural = _('Withdrawals')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self) -> str:
        return f"Withdrawal ${self.amount} by {self.user} [{self.status}]"
