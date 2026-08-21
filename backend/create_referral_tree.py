import os
import sys
import random
from decimal import Decimal

# Ensure backend root is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Initialize Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.getenv('DJANGO_SETTINGS_MODULE', 'config.settings.development'))
import django
django.setup()

from django.utils import timezone
from django.db import transaction
from apps.accounts.models import User
from apps.investments.models import Plan, Investment, NetworkChoices
from apps.investments.services import activate_investment, distribute_direct_income, update_user_active_level
from apps.wallet.models import Wallet

COUNTRIES = [
    'United States', 'United Kingdom', 'Germany', 'Singapore', 'United Arab Emirates',
    'Canada', 'Australia', 'Japan', 'Switzerland', 'France', 'Netherlands', 'Brazil'
]

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

def get_or_create_user(email, username, first_name='', last_name='', country=None, kyc_status=User.KYCStatus.APPROVED, parent=None):
    user = User.objects.filter(email=email).first()
    if user:
        updated = False
        if parent and user.parent != parent:
            user.parent = parent
            updated = True
        if first_name and user.first_name != first_name:
            user.first_name = first_name
            updated = True
        if last_name and user.last_name != last_name:
            user.last_name = last_name
            updated = True
        if country and user.country != country:
            user.country = country
            updated = True
        if updated:
            user.save()
        return user
    
    country = country or random.choice(COUNTRIES)
    user = User.objects.create_user(
        email=email,
        username=username,
        password='password123',
        first_name=first_name,
        last_name=last_name,
        country=country,
        kyc_status=kyc_status,
        parent=parent,
        is_email_verified=True
    )
    return user

def create_and_activate_investment(user, plan, amount, admin_user, tx_hash_suffix):
    # Check if user already has an active investment in this plan
    existing = Investment.objects.filter(user=user, plan=plan, status=Investment.Status.ACTIVE).first()
    if existing:
        return existing

    amount = Decimal(str(amount))
    max_return = (amount * Decimal('3.00')).quantize(Decimal('0.01'))
    tx_hash = f"0x{user.username[:6].lower()}{tx_hash_suffix}{random.randint(100000, 999999)}abcdef"
    sender_addr = f"0x{user.username[:4].lower()}{random.randint(10000000, 99999999)}0000000000000000"

    investment = Investment.objects.create(
        user=user,
        plan=plan,
        amount=amount,
        max_return=max_return,
        status=Investment.Status.DEPOSIT_PENDING,
        deposit_network=NetworkChoices.BEP20,
        deposit_txn_hash=tx_hash,
        deposit_sender_address=sender_addr,
        deposit_submitted_at=timezone.now(),
    )

    # 1. Activate investment (updates wallet total_invested / deposited)
    activate_investment(investment, admin_user)

    # 2. Distribute direct commissions to upline
    distribute_direct_income(investment)
    
    # 3. Update sponsor active levels
    curr = user.parent
    while curr:
        update_user_active_level(curr)
        curr = curr.parent

    return investment

def run_seed():
    print("=" * 65)
    print("🚀 FINOVO: SEEDING EXTENSIVE MULTI-TIER REFERRAL NETWORK")
    print("=" * 65)

    admin_user = get_or_create_admin()
    print(f"✔ Admin Superuser: {admin_user.email}")

    # 1. Plans
    print("\n--- 1. Setting up Investment Plans ---")
    plans = get_or_create_plans()
    for name, p in plans.items():
        print(f"  • {p.name.ljust(14)} | Min: ${p.minimum_amount} | Max: ${p.maximum_amount} | ROI: {p.weekly_roi_rate}%/wk")

    print("\n--- 2. Building Hierarchical Referral Tree (Top-Down) ---")
    
    created_count = 0
    invested_count = 0

    # -------------------------------------------------------------
    # BRANCH 1: Global Ambassador Victor Vance (Unlocks Level 5!)
    # -------------------------------------------------------------
    victor = get_or_create_user('whale.victor@finovo.com', 'victor_whale', 'Victor', 'Vance', 'United Kingdom')
    create_and_activate_investment(victor, plans['Elite Plan'], Decimal('10000.00'), admin_user, 'vic01')
    created_count += 1
    invested_count += 1

    # Victor's 12 Directs (L1) -> satisfies 10 directs needed for Level 5
    victor_directs_data = [
        ('david.ross@finovo.com', 'david_ross', 'David', 'Ross', 'United States', plans['Elite Plan'], 5000),
        ('elena.rostova@finovo.com', 'elena_r', 'Elena', 'Rostova', 'Germany', plans['Elite Plan'], 4000),
        ('marcus.aurelius@finovo.com', 'marcus_a', 'Marcus', 'Aurelius', 'Switzerland', plans['Pro Plan'], 3000),
        ('sophia.martinez@finovo.com', 'sophia_m', 'Sophia', 'Martinez', 'Spain', plans['Pro Plan'], 2500),
        ('james.wilson@finovo.com', 'james_w', 'James', 'Wilson', 'Canada', plans['Pro Plan'], 2000),
        ('olivia.taylor@finovo.com', 'olivia_t', 'Olivia', 'Taylor', 'Australia', plans['Pro Plan'], 1500),
        ('alex.turner@finovo.com', 'alex_t', 'Alex', 'Turner', 'Singapore', plans['Pro Plan'], 1000),
        ('chloe.bennett@finovo.com', 'chloe_b', 'Chloe', 'Bennett', 'United States', plans['Starter Plan'], 800),
        ('ryan.cooper@finovo.com', 'ryan_c', 'Ryan', 'Cooper', 'United Kingdom', plans['Starter Plan'], 500),
        ('emma.watson@finovo.com', 'emma_w', 'Emma', 'Watson', 'France', plans['Starter Plan'], 500),
        ('daniel.craig@finovo.com', 'daniel_c', 'Daniel', 'Craig', 'United Arab Emirates', plans['Starter Plan'], 300),
        ('mia.khalil@finovo.com', 'mia_k', 'Mia', 'Khalil', 'United Arab Emirates', plans['Starter Plan'], 200),
    ]

    victor_l1_users = []
    for email, uname, fn, ln, ctry, plan, amt in victor_directs_data:
        u = get_or_create_user(email, uname, fn, ln, ctry, parent=victor)
        create_and_activate_investment(u, plan, Decimal(str(amt)), admin_user, 'v_l1')
        victor_l1_users.append(u)
        created_count += 1
        invested_count += 1

    # David Ross Downlines (L2 -> L3 -> L4 -> L5 -> L6)
    david = victor_l1_users[0]
    david_sub_users = []
    for i in range(1, 7):
        u = get_or_create_user(f'david.team{i}@finovo.com', f'd_team{i}', f'DavidL2_{i}', 'Member', parent=david)
        create_and_activate_investment(u, plans['Pro Plan'] if i <= 2 else plans['Starter Plan'], Decimal(str(300 * i)), admin_user, f'd_l2_{i}')
        david_sub_users.append(u)
        created_count += 1
        invested_count += 1

    # L3 under david.team1 & david.team2
    l3_david_users = []
    for parent_u in david_sub_users[:3]:
        for j in range(1, 4):
            u = get_or_create_user(f'{parent_u.username}.sub{j}@finovo.com', f'{parent_u.username}_s{j}', f'L3_{parent_u.username}', f'M{j}', parent=parent_u)
            create_and_activate_investment(u, plans['Starter Plan'], Decimal('350.00'), admin_user, f'd_l3_{j}')
            l3_david_users.append(u)
            created_count += 1
            invested_count += 1

    # L4 under first 3 L3 users
    l4_david_users = []
    for parent_u in l3_david_users[:3]:
        for k in range(1, 3):
            u = get_or_create_user(f'{parent_u.username}.l4_{k}@finovo.com', f'{parent_u.username}_l4_{k}', f'L4', f'Node{k}', parent=parent_u)
            create_and_activate_investment(u, plans['Starter Plan'], Decimal('250.00'), admin_user, f'd_l4_{k}')
            l4_david_users.append(u)
            created_count += 1
            invested_count += 1

    # L5 & L6 under L4
    l5_u = get_or_create_user('david.deep.l5@finovo.com', 'd_deep_l5', 'DavidDeep', 'L5', parent=l4_david_users[0])
    create_and_activate_investment(l5_u, plans['Starter Plan'], Decimal('200.00'), admin_user, 'd_l5')
    created_count += 1
    invested_count += 1

    l6_u = get_or_create_user('david.deep.l6@finovo.com', 'd_deep_l6', 'DavidDeep', 'L6', parent=l5_u)
    create_and_activate_investment(l6_u, plans['Starter Plan'], Decimal('150.00'), admin_user, 'd_l6')
    created_count += 1
    invested_count += 1

    # Elena Rostova Downlines (L2 -> L3)
    elena = victor_l1_users[1]
    for i in range(1, 6):
        u2 = get_or_create_user(f'elena.team{i}@finovo.com', f'e_team{i}', f'ElenaL2_{i}', 'Investor', parent=elena)
        create_and_activate_investment(u2, plans['Pro Plan'] if i == 1 else plans['Starter Plan'], Decimal('400.00'), admin_user, f'e_l2_{i}')
        created_count += 1
        invested_count += 1
        for j in range(1, 3):
            u3 = get_or_create_user(f'elena.team{i}.sub{j}@finovo.com', f'e_t{i}_s{j}', f'ElenaL3', f'Member{j}', parent=u2)
            create_and_activate_investment(u3, plans['Starter Plan'], Decimal('200.00'), admin_user, f'e_l3_{j}')
            created_count += 1
            invested_count += 1

    # Marcus Aurelius Downlines
    marcus = victor_l1_users[2]
    for i in range(1, 5):
        um = get_or_create_user(f'marcus.team{i}@finovo.com', f'm_team{i}', f'MarcusL2_{i}', 'Trader', parent=marcus)
        create_and_activate_investment(um, plans['Starter Plan'], Decimal('300.00'), admin_user, f'm_l2_{i}')
        created_count += 1
        invested_count += 1

    # -------------------------------------------------------------
    # BRANCH 2: VP Network Sarah Connor (Unlocks Level 4!)
    # -------------------------------------------------------------
    sarah = get_or_create_user('sarah.investor@finovo.com', 'sarah_c', 'Sarah', 'Connor', 'United States')
    create_and_activate_investment(sarah, plans['Elite Plan'], Decimal('6000.00'), admin_user, 'sarah01')
    created_count += 1
    invested_count += 1

    sarah_directs = [
        ('liam.neeson@finovo.com', 'liam_n', 'Liam', 'Neeson', 'Ireland', plans['Pro Plan'], 2000),
        ('noah.centineo@finovo.com', 'noah_c', 'Noah', 'Centineo', 'Canada', plans['Pro Plan'], 1500),
        ('ava.gardner@finovo.com', 'ava_g', 'Ava', 'Gardner', 'United States', plans['Pro Plan'], 1000),
        ('isabella.ross@finovo.com', 'isabella_r', 'Isabella', 'Ross', 'Italy', plans['Starter Plan'], 800),
        ('lucas.scott@finovo.com', 'lucas_s', 'Lucas', 'Scott', 'Australia', plans['Starter Plan'], 500),
        ('mason.mount@finovo.com', 'mason_m', 'Mason', 'Mount', 'United Kingdom', plans['Starter Plan'], 400),
        ('harper.lee@finovo.com', 'harper_l', 'Harper', 'Lee', 'United States', plans['Starter Plan'], 300),
        ('evelyn.salt@finovo.com', 'evelyn_s', 'Evelyn', 'Salt', 'Germany', plans['Starter Plan'], 200),
    ]

    sarah_l1_users = []
    for email, uname, fn, ln, ctry, plan, amt in sarah_directs:
        u = get_or_create_user(email, uname, fn, ln, ctry, parent=sarah)
        create_and_activate_investment(u, plan, Decimal(str(amt)), admin_user, 's_l1')
        sarah_l1_users.append(u)
        created_count += 1
        invested_count += 1

    # Sub-teams under Liam
    liam = sarah_l1_users[0]
    for i in range(1, 5):
        ul = get_or_create_user(f'liam.team{i}@finovo.com', f'l_team{i}', f'LiamL2_{i}', 'Member', parent=liam)
        create_and_activate_investment(ul, plans['Starter Plan'], Decimal('450.00'), admin_user, f'l_l2_{i}')
        created_count += 1
        invested_count += 1
        for j in range(1, 3):
            ul3 = get_or_create_user(f'liam.t{i}.sub{j}@finovo.com', f'l_t{i}_s{j}', f'LiamL3', f'Member{j}', parent=ul)
            create_and_activate_investment(ul3, plans['Starter Plan'], Decimal('200.00'), admin_user, f'l_l3_{j}')
            created_count += 1
            invested_count += 1

    # -------------------------------------------------------------
    # BRANCH 3: Crypto Pioneer Arthur Pendelton (Level 3 Unlocked)
    # -------------------------------------------------------------
    arthur = get_or_create_user('crypto.king@finovo.com', 'crypto_arthur', 'Arthur', 'Pendelton', 'Switzerland')
    create_and_activate_investment(arthur, plans['Elite Plan'], Decimal('8000.00'), admin_user, 'art01')
    created_count += 1
    invested_count += 1

    crypto_directs = [
        ('satoshi.nak@finovo.com', 'satoshi_n', 'Satoshi', 'Nakamoto', 'Japan', plans['Elite Plan'], 5000),
        ('vitalik.eth@finovo.com', 'vitalik_b', 'Vitalik', 'Buterin', 'Canada', plans['Elite Plan'], 4000),
        ('charles.ada@finovo.com', 'charles_h', 'Charles', 'Hoskinson', 'United States', plans['Pro Plan'], 2500),
        ('gavin.dot@finovo.com', 'gavin_w', 'Gavin', 'Wood', 'United Kingdom', plans['Pro Plan'], 2000),
        ('anatoly.sol@finovo.com', 'anatoly_y', 'Anatoly', 'Yakovenko', 'United States', plans['Pro Plan'], 1500),
        ('sergey.link@finovo.com', 'sergey_n', 'Sergey', 'Nazarov', 'United States', plans['Starter Plan'], 900),
    ]

    crypto_l1_users = []
    for email, uname, fn, ln, ctry, plan, amt in crypto_directs:
        u = get_or_create_user(email, uname, fn, ln, ctry, parent=arthur)
        create_and_activate_investment(u, plan, Decimal(str(amt)), admin_user, 'c_l1')
        crypto_l1_users.append(u)
        created_count += 1
        invested_count += 1

    # Satoshi deep tree
    satoshi = crypto_l1_users[0]
    for i in range(1, 5):
        usat = get_or_create_user(f'sat.team{i}@finovo.com', f'sat_t{i}', f'SatL2_{i}', 'Dev', parent=satoshi)
        create_and_activate_investment(usat, plans['Pro Plan'] if i <= 2 else plans['Starter Plan'], Decimal('600.00'), admin_user, f'sat_l2_{i}')
        created_count += 1
        invested_count += 1
        for j in range(1, 3):
            usat3 = get_or_create_user(f'sat.t{i}.sub{j}@finovo.com', f'sat_t{i}_s{j}', f'SatL3', f'Node{j}', parent=usat)
            create_and_activate_investment(usat3, plans['Starter Plan'], Decimal('300.00'), admin_user, f'sat_l3_{j}')
            created_count += 1
            invested_count += 1

    # -------------------------------------------------------------
    # BRANCH 4: Legacy Test Network (root@finovo.com -> l1 -> l2 -> l3 -> l4 -> l5 -> l6)
    # -------------------------------------------------------------
    root = get_or_create_user('root@finovo.com', 'root', 'Root', 'Master', 'United States')
    create_and_activate_investment(root, plans['Elite Plan'], Decimal('3000.00'), admin_user, 'root01')
    created_count += 1
    invested_count += 1

    l1_a = get_or_create_user('l1_a@finovo.com', 'l1_a', 'Level1', 'Alpha', parent=root)
    l1_b = get_or_create_user('l1_b@finovo.com', 'l1_b', 'Level1', 'Beta', parent=root)
    l1_c = get_or_create_user('l1_c@finovo.com', 'l1_c', 'Level1', 'Gamma', parent=root)
    l1_d = get_or_create_user('l1_d@finovo.com', 'l1_d', 'Level1', 'Delta', parent=root)
    l1_e = get_or_create_user('l1_e@finovo.com', 'l1_e', 'Level1', 'Epsilon', parent=root)
    l1_f = get_or_create_user('l1_f@finovo.com', 'l1_f', 'Level1', 'Zeta', parent=root)

    create_and_activate_investment(l1_a, plans['Elite Plan'], Decimal('1500.00'), admin_user, 'l1a01')
    create_and_activate_investment(l1_b, plans['Pro Plan'], Decimal('800.00'), admin_user, 'l1b01')
    create_and_activate_investment(l1_c, plans['Pro Plan'], Decimal('600.00'), admin_user, 'l1c01')
    create_and_activate_investment(l1_d, plans['Starter Plan'], Decimal('400.00'), admin_user, 'l1d01')
    create_and_activate_investment(l1_e, plans['Starter Plan'], Decimal('300.00'), admin_user, 'l1e01')
    create_and_activate_investment(l1_f, plans['Starter Plan'], Decimal('200.00'), admin_user, 'l1f01')
    created_count += 6
    invested_count += 6

    l2_a1 = get_or_create_user('l2_a1@finovo.com', 'l2_a1', 'Level2', 'A1', parent=l1_a)
    l2_a2 = get_or_create_user('l2_a2@finovo.com', 'l2_a2', 'Level2', 'A2', parent=l1_a)
    l2_a3 = get_or_create_user('l2_a3@finovo.com', 'l2_a3', 'Level2', 'A3', parent=l1_a)
    l2_a4 = get_or_create_user('l2_a4@finovo.com', 'l2_a4', 'Level2', 'A4', parent=l1_a)
    create_and_activate_investment(l2_a1, plans['Pro Plan'], Decimal('700.00'), admin_user, 'l2a101')
    create_and_activate_investment(l2_a2, plans['Starter Plan'], Decimal('350.00'), admin_user, 'l2a201')
    create_and_activate_investment(l2_a3, plans['Starter Plan'], Decimal('250.00'), admin_user, 'l2a301')
    create_and_activate_investment(l2_a4, plans['Starter Plan'], Decimal('200.00'), admin_user, 'l2a401')
    created_count += 4
    invested_count += 4

    l3_a1 = get_or_create_user('l3_a1@finovo.com', 'l3_a1', 'Level3', 'A1', parent=l2_a1)
    l3_a2 = get_or_create_user('l3_a2@finovo.com', 'l3_a2', 'Level3', 'A2', parent=l2_a1)
    create_and_activate_investment(l3_a1, plans['Starter Plan'], Decimal('400.00'), admin_user, 'l3a101')
    create_and_activate_investment(l3_a2, plans['Starter Plan'], Decimal('300.00'), admin_user, 'l3a201')
    created_count += 2
    invested_count += 2

    l4_a1 = get_or_create_user('l4_a1@finovo.com', 'l4_a1', 'Level4', 'A1', parent=l3_a1)
    l4_a2 = get_or_create_user('l4_a2@finovo.com', 'l4_a2', 'Level4', 'A2', parent=l3_a1)
    create_and_activate_investment(l4_a1, plans['Starter Plan'], Decimal('250.00'), admin_user, 'l4a101')
    create_and_activate_investment(l4_a2, plans['Starter Plan'], Decimal('200.00'), admin_user, 'l4a201')
    created_count += 2
    invested_count += 2

    l5_a1 = get_or_create_user('l5_a1@finovo.com', 'l5_a1', 'Level5', 'A1', parent=l4_a1)
    create_and_activate_investment(l5_a1, plans['Starter Plan'], Decimal('150.00'), admin_user, 'l5a101')
    created_count += 1
    invested_count += 1

    l6_a1 = get_or_create_user('l6_a1@finovo.com', 'l6_a1', 'Level6', 'A1', parent=l5_a1)
    create_and_activate_investment(l6_a1, plans['Starter Plan'], Decimal('100.00'), admin_user, 'l6a101')
    created_count += 1
    invested_count += 1

    # -------------------------------------------------------------
    # 5. Unfunded / Prospective Users (Demonstrates Conversion Funnel)
    # -------------------------------------------------------------
    prospect_names = [
        ('prospect1@finovo.com', 'prospect1', 'Lucas', 'Perez', victor),
        ('prospect2@finovo.com', 'prospect2', 'Zara', 'Khan', sarah),
        ('prospect3@finovo.com', 'prospect3', 'Mateo', 'Silva', david),
        ('prospect4@finovo.com', 'prospect4', 'Amina', 'Diallo', elena),
        ('prospect5@finovo.com', 'prospect5', 'Ethan', 'Hunt', root),
    ]
    for email, uname, fn, ln, prnt in prospect_names:
        get_or_create_user(email, uname, fn, ln, parent=prnt, kyc_status=User.KYCStatus.PENDING)
        created_count += 1

    # Recalculate levels for all roots & key leaders
    for u in [victor, sarah, arthur, david, elena, marcus, liam, satoshi, root, l1_a, l2_a1, l3_a1, l4_a1, l5_a1]:
        update_user_active_level(u)

    # -------------------------------------------------------------
    # 6. Comprehensive Summary Output
    # -------------------------------------------------------------
    total_users = User.objects.count()
    total_investments = Investment.objects.count()
    active_investments = Investment.objects.filter(status=Investment.Status.ACTIVE).count()
    
    from django.db.models import Sum
    total_vol = Investment.objects.filter(status=Investment.Status.ACTIVE).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_commissions = Wallet.objects.aggregate(total=Sum('total_direct_income'))['total'] or Decimal('0.00')

    print("\n" + "=" * 65)
    print("📊 SEEDING COMPLETE — NETWORK SUMMARY")
    print("=" * 65)
    print(f"  • Total Registered Users:      {total_users}")
    print(f"  • Active Investments:          {active_investments} / {total_investments}")
    print(f"  • Total Capital Invested:      ${total_vol:,.2f}")
    print(f"  • Direct Commissions Paid:     ${total_commissions:,.2f}")
    print("=" * 65)

    print("\n👑 TOP NETWORK LEADERS & SPONSOR RANKS:")
    leaders = [victor, sarah, arthur, david, elena, marcus, liam, satoshi, root]
    for leader in leaders:
        leader.refresh_from_db()
        wallet, _ = Wallet.objects.get_or_create(user=leader)
        directs_count = leader.direct_children.count()
        active_directs = leader.direct_children.filter(investments__status=Investment.Status.ACTIVE).distinct().count()
        print(f"\n  👤 {leader.full_name} ({leader.email})")
        print(f"     Rank: Level {leader.active_level} Sponsor | Directs: {active_directs} active / {directs_count} total")
        print(f"     Direct Income: ${wallet.total_direct_income:,.2f} | Balance: ${wallet.balance:,.2f} | Invested: ${wallet.total_invested:,.2f}")

    print("\n" + "=" * 65)
    print("🔑 KEY TEST ACCOUNTS (Password for all: 'password123')")
    print("=" * 65)
    print("  • Admin:              admin@finovo.com (Superuser, Admin Portal)")
    print("  • Global Ambassador:  whale.victor@finovo.com (Level 5 Rank, 12 Directs, $10k Plan)")
    print("  • VP Network Leader:  sarah.investor@finovo.com (Level 4 Rank, 8 Directs, $6k Plan)")
    print("  • Crypto Founder:     crypto.king@finovo.com (Level 3 Rank, 6 Directs, $8k Plan)")
    print("  • L1 Branch Leader:   david.ross@finovo.com (Deep 6-Level Downline Team)")
    print("  • Legacy Test Root:   root@finovo.com (Multi-tier Downline)")
    print("=================================================================\n")

if __name__ == '__main__':
    run_seed()
