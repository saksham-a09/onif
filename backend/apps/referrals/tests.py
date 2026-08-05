from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.referrals.models import ReferralRelationship, ReferralCommission

User = get_user_model()


class ReferralsModelTests(TestCase):
    def setUp(self):
        self.sponsor = User.objects.create_user(email='sponsor@example.com', username='sponsor')
        self.ref_user = User.objects.create_user(email='refuser@example.com', username='refuser', parent=self.sponsor)

    def test_referral_relationship_creation(self):
        rel = ReferralRelationship.objects.create(user=self.ref_user, sponsor=self.sponsor)
        self.assertEqual(rel.sponsor, self.sponsor)

    def test_referral_commission_creation(self):
        comm = ReferralCommission.objects.create(
            user=self.sponsor,
            from_user=self.ref_user,
            amount=Decimal('2.40'),
            level=1,
            commission_type=ReferralCommission.CommissionType.DIRECT
        )
        self.assertFalse(comm.is_paid)
        self.assertEqual(comm.amount, Decimal('2.40'))
