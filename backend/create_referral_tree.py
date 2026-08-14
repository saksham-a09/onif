import os
import django
from decimal import Decimal

# Initialize Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.utils import timezone
from apps.accounts.models import User
from apps.investments.models import Plan, Investment, NetworkChoices
from apps.investments.services import activate_investment, distribute_direct_income, update_user_active_level
from apps.wallet.models import Wallet

def get_or_create_admin():
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.filter(email='admin@finovo.com').first()
    if not admin_user:
        admin_user = User.objects.create_superuser(
            email='admin@finovo.com',
            username='admin',
            password='adminpassword123'
        )
    return admin_user

def get_or_create_plans():
    plans = {
        'Starter Plan': {
            'description': 'Institutional starter yield plan with weekly ROI.',
            'minimum_amount': Decimal('100.00'),
            'maximum_amount': Decimal('1000.00'),
            'max_total_return': Decimal('3000.00'),
            'weekly_roi_rate': Decimal('2.50'),
            'duration_weeks': 120,
            'is_active': True,
        },
        'Pro Plan': {
            'description': 'High-performance growth plan with accelerated returns.',
            'minimum_amount': Decimal('500.00'),
            'maximum_amount': Decimal('5000.00'),
            'max_total_return': Decimal('15000.00'),
            'weekly_roi_rate': Decimal('3.50'),
            'duration_weeks': 120,
            'is_active': True,
        },
        'Elite Plan': {
            'description': 'Ultra-tier institutional wealth management plan.',
            'minimum_amount': Decimal('1000.00'),
            'maximum_amount': Decimal('10000.00'),
            'max_total_return': Decimal('30000.00'),
            'weekly_roi_rate': Decimal('5.00'),
            'duration_weeks': 120,
            'is_active': True,
        },
    }

    created_plans = {}
    for name, data in plans.items():
        plan, _ = Plan.objects.update_or_create(name=name, defaults=data)
        created_plans[name] = plan
    return created_plans

def get_or_create_user(email, username, parent=None):
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        if parent and user.parent != parent:
            user.parent = parent
            user.save(update_fields=['parent'])
        return user
    
    user = User.objects.create_user(
        email=email,
        username=username,
        password='password123',
        parent=parent,
        is_email_verified=True
    )
    return user

def create_and_activate_investment(user, plan, amount, admin_user, tx_hash_suffix):
    # Check if user already has an active investment in this plan
    existing = Investment.objects.filter(user=user, plan=plan, status=Investment.Status.ACTIVE).first()
    if existing:
        print(f"  → {user.email} already has active investment #{str(existing.id)[:8]} (${existing.amount}) in {plan.name}")
        return existing

    max_return = (amount * Decimal('3.00')).quantize(Decimal('0.01'))
    investment = Investment.objects.create(
        user=user,
        plan=plan,
        amount=amount,
        max_return=max_return,
        status=Investment.Status.DEPOSIT_PENDING,
        deposit_network=NetworkChoices.BEP20,
        deposit_txn_hash=f"0x{user.username[:6].lower()}{tx_hash_suffix}789abcdef1234567890",
        deposit_sender_address=f"0x{user.username[:4].lower()}sender000000000000000000000",
        deposit_submitted_at=timezone.now(),
    )

    # 1. Activate investment (updates wallet total_invested / deposited)
    activate_investment(investment, admin_user)

    # 2. Distribute direct commissions to upline
    commissions = distribute_direct_income(investment)
    
    # 3. Update sponsor active levels
    curr = user.parent
    while curr:
        update_user_active_level(curr)
        curr = curr.parent

    print(f"  ✔ Created & Activated ${amount} ({plan.name}) for {user.email} -> {len(commissions)} direct commission(s) paid")
    return investment

def run_seed():
    print("==================================================")
    print("FINOVO: SEEDING REFERRAL TREE & INVESTMENTS")
    print("==================================================")

    admin_user = get_or_create_admin()
    print(f"Admin User: {admin_user.email}")

    # 1. Plans
    print("\n--- 1. Setting up Investment Plans ---")
    plans = get_or_create_plans()
    for name, p in plans.items():
        print(f"Plan: {p.name} | Min: ${p.minimum_amount} | Max: ${p.maximum_amount} | ROI: {p.weekly_roi_rate}%/wk")

    # 2. Users (Created top-down)
    print("\n--- 2. Setting up Referral Hierarchy ---")
    root = get_or_create_user('root@finovo.com', 'root')
    l1_a = get_or_create_user('l1_a@finovo.com', 'l1_a', parent=root)
    l1_b = get_or_create_user('l1_b@finovo.com', 'l1_b', parent=root)
    l2_a1 = get_or_create_user('l2_a1@finovo.com', 'l2_a1', parent=l1_a)
    l2_a2 = get_or_create_user('l2_a2@finovo.com', 'l2_a2', parent=l1_a)
    l3_a1 = get_or_create_user('l3_a1@finovo.com', 'l3_a1', parent=l2_a1)
    l4_a1 = get_or_create_user('l4_a1@finovo.com', 'l4_a1', parent=l3_a1)
    l5_a1 = get_or_create_user('l5_a1@finovo.com', 'l5_a1', parent=l4_a1)

    print("Referral hierarchy is ready.")

    # 3. Create & Activate Investments Top-Down
    # (Top-down ensures sponsors have active investments before children invest)
    print("\n--- 3. Creating & Activating Investments (Top-Down) ---")
    create_and_activate_investment(root, plans['Elite Plan'], Decimal('2000.00'), admin_user, 'root01')
    create_and_activate_investment(l1_a, plans['Elite Plan'], Decimal('1000.00'), admin_user, 'l1a01')
    create_and_activate_investment(l1_b, plans['Pro Plan'], Decimal('500.00'), admin_user, 'l1b01')
    create_and_activate_investment(l2_a1, plans['Pro Plan'], Decimal('500.00'), admin_user, 'l2a101')
    create_and_activate_investment(l2_a2, plans['Starter Plan'], Decimal('200.00'), admin_user, 'l2a201')
    create_and_activate_investment(l3_a1, plans['Starter Plan'], Decimal('300.00'), admin_user, 'l3a101')
    create_and_activate_investment(l4_a1, plans['Starter Plan'], Decimal('200.00'), admin_user, 'l4a101')
    create_and_activate_investment(l5_a1, plans['Starter Plan'], Decimal('100.00'), admin_user, 'l5a101')

    # 4. Summary Output
    print("\n==================================================")
    print("TREE, WALLETS & COMMISSION SUMMARY")
    print("==================================================")
    all_users = [root, l1_a, l1_b, l2_a1, l2_a2, l3_a1, l4_a1, l5_a1]
    
    for u in all_users:
        u.refresh_from_db()
        wallet, _ = Wallet.objects.get_or_create(user=u)
        active_inv = u.investments.filter(status=Investment.Status.ACTIVE).first()
        inv_str = f"${active_inv.amount} ({active_inv.plan.name}) [Credited: ${active_inv.total_credited}/${active_inv.max_return}]" if active_inv else "None"
        parent_str = u.parent.email if u.parent else "None (Root)"
        print(f"\nUser: {u.email} (Level {u.active_level} Sponsor, Parent: {parent_str})")
        print(f"  Active Investment: {inv_str}")
        print(f"  Wallet Balance:    ${wallet.balance:.2f} (Spendable/Withdrawable)")
        print(f"  Direct Income:     ${wallet.total_direct_income:.2f}")
        print(f"  Total Invested:    ${wallet.total_invested:.2f}")

    print("\nAll accounts have password: 'password123'")
    print("==================================================")

if __name__ == '__main__':
    run_seed()
