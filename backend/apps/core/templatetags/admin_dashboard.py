from django import template
from django.contrib.auth import get_user_model
from django.db.models import Sum
from apps.transactions.models import Deposit, Withdrawal
from apps.investments.models import Investment
from apps.wallet.models import Wallet

register = template.Library()
User = get_user_model()

@register.inclusion_tag('admin/dashboard_stats.html')
def get_dashboard_stats():
    # Total Users
    total_users = User.objects.count()
    
    # Total Active Investments Amount
    active_investments = Investment.objects.filter(status=Investment.Status.ACTIVE).aggregate(total=Sum('amount'))['total'] or 0
    
    # Total Approved Deposits
    total_deposits = Deposit.objects.filter(status=Deposit.Status.APPROVED).aggregate(total=Sum('amount'))['total'] or 0
    
    # Total Processed Withdrawals
    total_withdrawals = Withdrawal.objects.filter(status=Withdrawal.Status.APPROVED).aggregate(total=Sum('net_amount'))['total'] or 0
    
    # Total System Wallet Balance (Liabilities)
    total_wallet_balances = Wallet.objects.aggregate(total=Sum('balance'))['total'] or 0
    
    return {
        'total_users': total_users,
        'active_investments': active_investments,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'total_wallet_balances': total_wallet_balances,
    }
