from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Sum
from apps.wallet.models import Wallet
from apps.investments.models import Investment
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Backfills team_total_members and team_total_investment for all wallets.'

    def handle(self, *args, **options):
        self.stdout.write('Starting backfill of team stats...')
        
        users = User.objects.all()
        total_users = users.count()
        
        for i, user in enumerate(users):
            # Calculate team
            l1 = list(User.objects.filter(parent=user).values_list('id', flat=True))
            l2 = list(User.objects.filter(parent_id__in=l1).values_list('id', flat=True)) if l1 else []
            l3 = list(User.objects.filter(parent_id__in=l2).values_list('id', flat=True)) if l2 else []
            l4 = list(User.objects.filter(parent_id__in=l3).values_list('id', flat=True)) if l3 else []
            l5 = list(User.objects.filter(parent_id__in=l4).values_list('id', flat=True)) if l4 else []
            
            all_ids = l1 + l2 + l3 + l4 + l5
            total_members = len(all_ids)
            
            if all_ids:
                total_inv = Investment.objects.filter(
                    user_id__in=all_ids,
                    status__in=[Investment.Status.ACTIVE, Investment.Status.COMPLETED]
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            else:
                total_inv = Decimal('0.00')
                
            wallet, _ = Wallet.objects.get_or_create(user=user)
            wallet.team_total_members = total_members
            wallet.team_total_investment = total_inv
            wallet.save(update_fields=['team_total_members', 'team_total_investment'])
            
            if (i + 1) % 100 == 0:
                self.stdout.write(f'Processed {i + 1}/{total_users} users.')
                
        self.stdout.write(self.style.SUCCESS('Successfully backfilled team stats for all users!'))
