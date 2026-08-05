import uuid
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator


class Plan(models.Model):
    """
    Investment plan created by admin.

    Defines the structure, limits, and return parameters for an investment product.
    All monetary limits are admin-configurable via PlatformSettings.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=100, verbose_name=_('Plan Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))

    minimum_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('120.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('Minimum Investment Amount ($)'),
    )
    maximum_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('10000.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('Maximum Investment Amount ($)'),
    )
    max_total_return = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('350.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('Maximum Total Return ($) (Capital Included)'),
        help_text=_('Investment stops crediting once this amount is reached. Default: $350'),
    )
    weekly_roi_rate = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name=_('Weekly ROI Rate (%)'),
        help_text=_('Percentage credited to wallet each Saturday'),
    )
    duration_weeks = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Duration (Weeks)'),
        help_text=_('0 means open-ended until max return is reached'),
    )
    is_active = models.BooleanField(default=True, db_index=True, verbose_name=_('Is Active'))

    class Meta:
        verbose_name = _('Investment Plan')
        verbose_name_plural = _('Investment Plans')
        ordering = ['name']

    def __str__(self) -> str:
        return f"{self.name} (min: ${self.minimum_amount})"


class Investment(models.Model):
    """
    A user's investment in a Plan.

    Lifecycle: PENDING → ACTIVE (admin approves) → COMPLETED (max return reached).
    total_credited tracks sum of all ROI payments. When total_credited >= max_return,
    the investment is marked COMPLETED.
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        ACTIVE = 'ACTIVE', _('Active')
        COMPLETED = 'COMPLETED', _('Completed')
        REJECTED = 'REJECTED', _('Rejected')
        CANCELLED = 'CANCELLED', _('Cancelled')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='investments',
        verbose_name=_('Investor'),
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='investments',
        verbose_name=_('Plan'),
    )

    # Financial fields — stored at time of investment, not re-calculated from Plan
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('Principal Amount ($)'),
    )
    max_return = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name=_('Maximum Total Return ($)'),
        help_text=_('Copied from plan at the time of investment'),
    )
    total_credited = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Total Credited ($)'),
        help_text=_('Running sum of all ROI payments made. Investment closes when this reaches max_return.'),
    )

    # Status & Approval
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name=_('Status'),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_investments',
        verbose_name=_('Approved By'),
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Approved At'))
    rejection_reason = models.TextField(blank=True, verbose_name=_('Rejection Reason'))

    # Timeline
    start_date = models.DateField(null=True, blank=True, verbose_name=_('Start Date'))
    end_date = models.DateField(null=True, blank=True, verbose_name=_('End Date'))
    last_roi_date = models.DateField(
        null=True, blank=True, verbose_name=_('Last ROI Date'),
        help_text=_('Date of the last weekly ROI distribution'),
    )

    class Meta:
        verbose_name = _('Investment')
        verbose_name_plural = _('Investments')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self) -> str:
        return f"{self.user} — ${self.amount} ({self.status})"

    @property
    def remaining_return(self) -> Decimal:
        """How much more can be credited before the investment completes."""
        return max(Decimal('0.00'), self.max_return - self.total_credited)

    @property
    def profit(self) -> Decimal:
        """Net profit (total credited minus principal)."""
        return max(Decimal('0.00'), self.total_credited - self.amount)
