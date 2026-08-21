from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ReferralRelationship, ReferralCommission

User = get_user_model()


class DirectMemberSerializer(serializers.ModelSerializer):
    """Minimal user info for team list."""
    total_refers = serializers.IntegerField(read_only=True, default=0)
    investment_sum = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True, default=0.00)
    direct_income_sum = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True, default=0.00)
    roi_income_sum = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True, default=0.00)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'full_name', 'is_active', 'active_level', 'date_joined',
            'total_refers', 'investment_sum', 'direct_income_sum', 'roi_income_sum'
        ]


class ReferralCommissionSerializer(serializers.ModelSerializer):
    from_user_email = serializers.EmailField(source='from_user.email', read_only=True)

    class Meta:
        model = ReferralCommission
        fields = [
            'id', 'from_user_email', 'amount', 'level', 'commission_type',
            'is_paid', 'created_at',
        ]
        read_only_fields = fields
