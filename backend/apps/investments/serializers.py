from decimal import Decimal
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

    class Meta:
        model = Investment
        fields = [
            'id', 'plan', 'plan_name', 'amount', 'max_return', 'total_credited',
            'remaining_return', 'profit', 'status', 'start_date', 'end_date',
            'last_roi_date', 'created_at',
        ]
        read_only_fields = [
            'id', 'plan_name', 'max_return', 'total_credited', 'remaining_return',
            'profit', 'status', 'start_date', 'end_date', 'last_roi_date', 'created_at',
        ]


class InvestmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investment
        fields = ['plan', 'amount']

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
        return attrs

    def create(self, validated_data):
        plan = validated_data['plan']
        user = self.context['request'].user
        return Investment.objects.create(
            user=user,
            plan=plan,
            amount=validated_data['amount'],
            max_return=plan.max_total_return,
        )
