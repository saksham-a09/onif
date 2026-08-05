from rest_framework import serializers
from .models import Wallet, WalletTransaction


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = [
            'id', 'balance', 'total_deposited', 'total_withdrawn',
            'total_roi_earned', 'total_direct_income', 'total_referral_income',
            'total_invested', 'updated_at',
        ]
        read_only_fields = fields


class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = [
            'id', 'transaction_type', 'category', 'amount',
            'balance_before', 'balance_after', 'description',
            'reference_id', 'created_at',
        ]
        read_only_fields = fields
