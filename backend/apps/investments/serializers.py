from decimal import Decimal
from django.utils import timezone
from rest_framework import serializers
from .models import Plan, Investment


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            'id', 'name', 'description', 'minimum_amount', 'maximum_amount',
            'max_total_return', 'weekly_roi_rate', 'duration_weeks',
        ]
        read_only_fields = fields


class InvestmentSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    remaining_return = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    profit = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    deposit_proof_url = serializers.SerializerMethodField()

    class Meta:
        model = Investment
        fields = [
            'id', 'plan', 'plan_name', 'amount', 'max_return', 'total_credited',
            'remaining_return', 'profit', 'status',
            'deposit_network', 'deposit_txn_hash', 'deposit_sender_address',
            'deposit_proof', 'deposit_proof_url', 'deposit_submitted_at',
            'start_date', 'end_date', 'last_roi_date', 'created_at',
        ]
        read_only_fields = [
            'id', 'plan_name', 'max_return', 'total_credited', 'remaining_return',
            'profit', 'status', 'deposit_proof_url', 'deposit_submitted_at',
            'start_date', 'end_date', 'last_roi_date', 'created_at',
        ]

    def get_deposit_proof_url(self, obj) -> str | None:
        if obj.deposit_proof:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.deposit_proof.url)
            return obj.deposit_proof.url
        return None


class InvestmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new investment.

    The user picks a plan + amount and provides deposit proof (crypto payment
    details) in the same request. The investment is created with status
    DEPOSIT_PENDING until an admin approves the deposit.
    """

    class Meta:
        model = Investment
        fields = [
            'plan', 'amount',
            'deposit_network', 'deposit_txn_hash',
            'deposit_sender_address', 'deposit_proof',
        ]

    def validate_deposit_network(self, value):
        if not value:
            raise serializers.ValidationError('Deposit network is required.')
        return value

    def validate(self, attrs):
        plan = attrs['plan']
        amount = attrs['amount']

        if not plan.is_active:
            raise serializers.ValidationError({'plan': 'This investment plan is not currently active.'})

        if amount < plan.minimum_amount:
            raise serializers.ValidationError(
                {'amount': f'Minimum investment for this plan is ${plan.minimum_amount}.'}
            )
        if amount > plan.maximum_amount:
            raise serializers.ValidationError(
                {'amount': f'Maximum investment for this plan is ${plan.maximum_amount}.'}
            )

        if not attrs.get('deposit_txn_hash') and not attrs.get('deposit_proof'):
            raise serializers.ValidationError(
                'Please provide either a transaction hash or a deposit proof screenshot.'
            )

        return attrs

    def create(self, validated_data):
        plan = validated_data['plan']
        user = self.context['request'].user
        return Investment.objects.create(
            user=user,
            plan=plan,
            amount=validated_data['amount'],
            max_return=plan.max_total_return,
            status=Investment.Status.DEPOSIT_PENDING,
            deposit_network=validated_data.get('deposit_network', ''),
            deposit_txn_hash=validated_data.get('deposit_txn_hash', ''),
            deposit_sender_address=validated_data.get('deposit_sender_address', ''),
            deposit_proof=validated_data.get('deposit_proof'),
            deposit_submitted_at=timezone.now(),
        )
