from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.investments.models import Plan, Investment

User = get_user_model()


class InvestmentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='investor@example.com', username='investor')
        self.plan = Plan.objects.create(
            name='Standard Plan',
            minimum_amount=Decimal('120.00'),
            maximum_amount=Decimal('5000.00'),
            max_total_return=Decimal('350.00'),
            weekly_roi_rate=Decimal('1.5')
        )

    def test_plan_creation(self):
        self.assertEqual(str(self.plan), 'Standard Plan (min: $120.00)')
        self.assertTrue(self.plan.is_active)

    def test_investment_creation_and_properties(self):
        investment = Investment.objects.create(
            user=self.user,
            plan=self.plan,
            amount=Decimal('120.00'),
            max_return=self.plan.max_total_return
        )
        self.assertEqual(investment.status, Investment.Status.PENDING)
        self.assertEqual(investment.remaining_return, Decimal('350.00'))
        self.assertEqual(investment.profit, Decimal('0.00'))

        # Credit ROI
        investment.total_credited = Decimal('200.00')
        investment.save()
        self.assertEqual(investment.remaining_return, Decimal('150.00'))
        self.assertEqual(investment.profit, Decimal('80.00'))
