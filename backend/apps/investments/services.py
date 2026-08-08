"""
ROI Engine Service Layer
=========================
Pure Python business logic for investment income distribution.
These functions are called by Celery tasks and admin actions.
All DB operations are atomic.
"""
from decimal import Decimal, ROUND_DOWN
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.core.models import PlatformSettings
from apps.investments.models import Investment
from apps.referrals.models import ReferralCommission
from apps.wallet.models import WalletTransaction
from apps.wallet.services import credit_wallet

User = get_user_model()


def _get_setting(key: str, default: str) -> Decimal:
    return Decimal(PlatformSettings.get(key, default))


def _level_unlock_threshold(level: int) -> int:
    """Return the number of active directs needed to unlock income at this level."""
    mapping = {
        1: int(PlatformSettings.get('LEVEL1_UNLOCK_DIRECTS', '2')),
        2: int(PlatformSettings.get('LEVEL2_UNLOCK_DIRECTS', '4')),
        3: int(PlatformSettings.get('LEVEL3_UNLOCK_DIRECTS', '6')),
        4: int(PlatformSettings.get('LEVEL4_UNLOCK_DIRECTS', '8')),
        5: int(PlatformSettings.get('LEVEL5_UNLOCK_DIRECTS', '10')),
    }
    return mapping.get(level, 999)


def _count_active_directs(user) -> int:
    """Count direct children who have at least one ACTIVE investment."""
    return user.direct_children.filter(
        investments__status=Investment.Status.ACTIVE
    ).distinct().count()


def update_user_active_level(user) -> int:
    """
    Recalculate and persist the user's active_level.
    Returns the new level (0–5).
    """
    active_directs = _count_active_directs(user)
    new_level = 0
    for lvl in range(1, 6):
        if active_directs >= _level_unlock_threshold(lvl):
            new_level = lvl
        else:
            break
    if user.active_level != new_level:
        User.objects.filter(pk=user.pk).update(active_level=new_level)
        user.active_level = new_level
    return new_level


@transaction.atomic
def distribute_direct_income(investment: Investment) -> list:
    """
    Distribute direct income (2% per level, up to 5 levels) upline
    when a new investment is APPROVED.

    Returns a list of ReferralCommission objects created.
    """
    rate = _get_setting('DIRECT_INCOME_RATE', '2.00') / Decimal('100')
    max_levels = int(PlatformSettings.get('MAX_REFERRAL_LEVELS', '5'))
    commissions_created = []

    current_user = investment.user
    for level in range(1, max_levels + 1):
        sponsor = current_user.parent
        if sponsor is None:
            break

        # Check level unlock
        active_directs = _count_active_directs(sponsor)
        required = _level_unlock_threshold(level)
        if active_directs < required:
            current_user = sponsor
            continue

        commission_amount = (investment.amount * rate).quantize(
            Decimal('0.01'), rounding=ROUND_DOWN
        )
        if commission_amount <= Decimal('0.00'):
            current_user = sponsor
            continue

        # Credit wallet
        credit_wallet(
            user=sponsor,
            amount=commission_amount,
            category=WalletTransaction.Category.DIRECT_INCOME,
            description=f'Level-{level} direct income from {investment.user.email}',
            reference_id=str(investment.id),
        )

        # Record commission
        comm = ReferralCommission.objects.create(
            user=sponsor,
            from_user=investment.user,
            investment=investment,
            amount=commission_amount,
            level=level,
            commission_type=ReferralCommission.CommissionType.DIRECT,
            is_paid=True,
        )
        commissions_created.append(comm)
        current_user = sponsor

    return commissions_created


@transaction.atomic
def distribute_roi_for_investment(investment: Investment) -> Decimal:
    """
    Calculate and credit the weekly ROI for a single ACTIVE investment.

    - Credits the investor's wallet (capped at remaining_return).
    - Marks the investment COMPLETED if max_return is reached.
    - Distributes ROI-level commissions (1.5% up to 5 levels) to upline.

    Returns the actual ROI amount credited (may be less than calculated if capped).
    """
    if investment.status != Investment.Status.ACTIVE:
        return Decimal('0.00')

    # Calculate weekly ROI
    roi_rate = investment.plan.weekly_roi_rate / Decimal('100')
    calculated_roi = (investment.amount * roi_rate).quantize(
        Decimal('0.01'), rounding=ROUND_DOWN
    )

    # Cap at remaining_return
    remaining = investment.remaining_return
    roi_amount = min(calculated_roi, remaining)

    if roi_amount <= Decimal('0.00'):
        return Decimal('0.00')

    # Credit investor wallet
    credit_wallet(
        user=investment.user,
        amount=roi_amount,
        category=WalletTransaction.Category.ROI,
        description=f'Weekly ROI from investment #{str(investment.id)[:8]}',
        reference_id=str(investment.id),
    )

    # Update investment
    investment.total_credited += roi_amount
    investment.last_roi_date = timezone.now().date()

    if investment.total_credited >= investment.max_return:
        investment.status = Investment.Status.COMPLETED
        investment.end_date = timezone.now().date()

    investment.save(update_fields=['total_credited', 'last_roi_date', 'status', 'end_date'])

    # Distribute ROI-level commissions upline (1.5% per level, 5 levels)
    _distribute_roi_commissions(investment, roi_amount)

    return roi_amount


def _distribute_roi_commissions(investment: Investment, roi_amount: Decimal) -> None:
    """Distribute ROI income commissions up the sponsor chain (5 levels, 1.5%)."""
    rate = _get_setting('ROI_INCOME_RATE', '1.50') / Decimal('100')
    max_levels = int(PlatformSettings.get('MAX_REFERRAL_LEVELS', '5'))

    current_user = investment.user
    for level in range(1, max_levels + 1):
        sponsor = current_user.parent
        if sponsor is None:
            break

        # Level unlock check
        active_directs = _count_active_directs(sponsor)
        required = _level_unlock_threshold(level)
        if active_directs < required:
            current_user = sponsor
            continue

        commission_amount = (roi_amount * rate).quantize(
            Decimal('0.01'), rounding=ROUND_DOWN
        )
        if commission_amount <= Decimal('0.00'):
            current_user = sponsor
            continue

        credit_wallet(
            user=sponsor,
            amount=commission_amount,
            category=WalletTransaction.Category.REFERRAL_INCOME,
            description=f'Level-{level} ROI commission from {investment.user.email}',
            reference_id=str(investment.id),
        )

        ReferralCommission.objects.create(
            user=sponsor,
            from_user=investment.user,
            investment=investment,
            amount=commission_amount,
            level=level,
            commission_type=ReferralCommission.CommissionType.ROI,
            is_paid=True,
        )
        current_user = sponsor
