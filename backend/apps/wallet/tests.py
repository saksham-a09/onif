from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.wallet.models import Wallet, WalletTransaction

User = get_user_model()


class WalletModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='walletuser@example.com', username='walletuser')
        self.wallet = Wallet.objects.create(user=self.user)

    def test_wallet_creation(self):
        self.assertEqual(self.wallet.balance, Decimal('0.00'))
        self.assertIn('walletuser@example.com', str(self.wallet))

    def test_wallet_transaction_creation(self):
        tx = WalletTransaction.objects.create(
            wallet=self.wallet,
            transaction_type=WalletTransaction.TransactionType.CREDIT,
            category=WalletTransaction.Category.DEPOSIT,
            amount=Decimal('100.00'),
            balance_before=Decimal('0.00'),
            balance_after=Decimal('100.00'),
            description='Test Deposit Credit'
        )
        self.assertEqual(tx.amount, Decimal('100.00'))
        self.assertEqual(tx.category, WalletTransaction.Category.DEPOSIT)
