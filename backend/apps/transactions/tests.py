from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.transactions.models import Deposit, Withdrawal, NetworkChoices

User = get_user_model()


class TransactionsModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='transuser@example.com', username='transuser')

    def test_deposit_creation(self):
        deposit = Deposit.objects.create(
            user=self.user,
            amount=Decimal('500.00'),
            network=NetworkChoices.BEP20,
            txn_hash='0x123abc'
        )
        self.assertEqual(deposit.status, Deposit.Status.PENDING)
        self.assertEqual(deposit.network, NetworkChoices.BEP20)

    def test_withdrawal_creation(self):
        withdrawal = Withdrawal.objects.create(
            user=self.user,
            amount=Decimal('50.00'),
            withdrawal_type=Withdrawal.WithdrawalType.PROFIT,
            fee=Decimal('1.00'),
            capital_charge=Decimal('0.00'),
            net_amount=Decimal('49.00'),
            network=NetworkChoices.TRC20,
            wallet_address='TXYZ123456789'
        )
        self.assertEqual(withdrawal.status, Withdrawal.Status.PENDING)
        self.assertEqual(withdrawal.net_amount, Decimal('49.00'))


class TransactionSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='ser@example.com', username='seruser')
        from apps.core.models import PlatformSettings
        PlatformSettings.objects.update_or_create(key='MIN_WITHDRAWAL', defaults={'value': '10.00'})
        PlatformSettings.objects.update_or_create(key='WITHDRAWAL_FEE', defaults={'value': '1.00'})

    def test_withdrawal_serializer_validation(self):
        from apps.transactions.serializers import WithdrawalSerializer
        from rest_framework.test import APIRequestFactory
        from apps.wallet.services import credit_wallet
        from apps.wallet.models import WalletTransaction
        
        request = APIRequestFactory().post('/')
        request.user = self.user
        
        # Insufficient balance test
        data = {
            'amount': '20.00',
            'withdrawal_type': Withdrawal.WithdrawalType.PROFIT,
            'network': NetworkChoices.TRC20,
            'wallet_address': 'TXYZ123'
        }
        serializer = WithdrawalSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('amount', serializer.errors)
        
        # Credit wallet and test successful validation
        credit_wallet(self.user, Decimal('50.00'), WalletTransaction.Category.DEPOSIT)
        
        serializer = WithdrawalSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['net_amount'], Decimal('19.00')) # 20 - 1 fee


from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

class TransactionViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='view@example.com', username='viewuser')
        self.client.force_authenticate(user=self.user)

    def test_list_deposits(self):
        self.user.is_staff = True
        self.user.save()
        url = reverse('deposit_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_withdrawal(self):
        from apps.core.models import PlatformSettings
        from apps.wallet.services import credit_wallet
        from apps.wallet.models import WalletTransaction
        
        PlatformSettings.objects.update_or_create(key='MIN_WITHDRAWAL', defaults={'value': '10.00'})
        PlatformSettings.objects.update_or_create(key='WITHDRAWAL_FEE', defaults={'value': '1.00'})
        credit_wallet(self.user, Decimal('50.00'), WalletTransaction.Category.DEPOSIT)
        
        url = reverse('withdrawal_list_create')
        data = {
            'amount': '15.00',
            'withdrawal_type': Withdrawal.WithdrawalType.PROFIT,
            'network': NetworkChoices.TRC20,
            'wallet_address': 'TXYZ123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TransactionAdminTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='adminuser@example.com', username='adminuser')
        self.admin = User.objects.create_superuser(email='super@example.com', username='super', password='123')
        
    def test_approve_withdrawal_admin_action(self):
        from apps.transactions.admin import WithdrawalAdmin
        from apps.wallet.services import credit_wallet
        from apps.wallet.models import WalletTransaction
        from django.contrib.admin.sites import AdminSite
        from django.test import RequestFactory
        
        # Setup data
        credit_wallet(self.user, Decimal('100.00'), WalletTransaction.Category.DEPOSIT)
        withdrawal = Withdrawal.objects.create(
            user=self.user,
            amount=Decimal('50.00'),
            withdrawal_type=Withdrawal.WithdrawalType.PROFIT,
            fee=Decimal('1.00'),
            capital_charge=Decimal('0.00'),
            net_amount=Decimal('49.00'),
            network=NetworkChoices.TRC20,
            wallet_address='TXYZ123456789'
        )
        
        admin_obj = WithdrawalAdmin(Withdrawal, AdminSite())
        request = RequestFactory().get('/admin/')
        request.user = self.admin
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        # Perform action
        queryset = Withdrawal.objects.filter(id=withdrawal.id)
        admin_obj.approve_withdrawals(request, queryset)
        
        # Verify
        withdrawal.refresh_from_db()
        self.assertEqual(withdrawal.status, Withdrawal.Status.APPROVED)
        
        self.user.wallet.refresh_from_db()
        self.assertEqual(self.user.wallet.balance, Decimal('50.00'))
