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
