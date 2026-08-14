from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.investments.models import Investment, Plan
from apps.transactions.models import Withdrawal, Deposit
from apps.wallet.models import Wallet, WalletTransaction
from apps.support.models import Ticket, TicketReply
from apps.core.models import PlatformSettings, AuditLog

User = get_user_model()


class AdminUserListSerializer(serializers.ModelSerializer):
    """Admin summary of registered users."""
    full_name = serializers.SerializerMethodField()
    parent_email = serializers.SerializerMethodField()
    wallet_balance = serializers.SerializerMethodField()
    total_invested = serializers.SerializerMethodField()
    active_investments_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'role', 'is_staff', 'is_superuser', 'kyc_status', 'is_email_verified',
            'referral_code', 'parent_email', 'active_level',
            'wallet_balance', 'total_invested', 'active_investments_count',
            'date_joined', 'created_at',
        ]

    def get_full_name(self, obj) -> str:
        return obj.full_name

    def get_parent_email(self, obj) -> str | None:
        return obj.parent.email if obj.parent else None

    def get_wallet_balance(self, obj) -> float:
        wallet = getattr(obj, 'wallet', None)
        return float(wallet.balance) if wallet else 0.0

    def get_total_invested(self, obj) -> float:
        wallet = getattr(obj, 'wallet', None)
        return float(wallet.total_invested) if wallet else 0.0

    def get_active_investments_count(self, obj) -> int:
        return obj.investments.filter(status=Investment.Status.ACTIVE).count()


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """Admin role / KYC / status updates."""
    class Meta:
        model = User
        fields = ['role', 'kyc_status', 'is_email_verified', 'is_staff', 'is_active']


class AdminBalanceAdjustmentSerializer(serializers.Serializer):
    """Manual admin credit or debit to a user's wallet."""
    action = serializers.ChoiceField(choices=['CREDIT', 'DEBIT'])
    amount = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=Decimal('0.01'))
    reason = serializers.CharField(max_length=255, required=True)


class AdminInvestmentSerializer(serializers.ModelSerializer):
    """Admin view for investments with deposit proof & user info."""
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    user_active_level = serializers.IntegerField(source='user.active_level', read_only=True)
    user_parent_email = serializers.SerializerMethodField()
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    plan_weekly_roi_rate = serializers.FloatField(source='plan.weekly_roi_rate', read_only=True)
    plan_duration_weeks = serializers.IntegerField(source='plan.duration_weeks', read_only=True)
    remaining_return = serializers.FloatField(read_only=True)
    progress_percent = serializers.SerializerMethodField()
    approved_by_email = serializers.SerializerMethodField()
    deposit_proof_url = serializers.SerializerMethodField()
    explorer_url = serializers.SerializerMethodField()

    class Meta:
        model = Investment
        fields = [
            'id', 'user_id', 'user_email', 'user_username', 'user_full_name',
            'user_active_level', 'user_parent_email',
            'plan_id', 'plan_name', 'plan_weekly_roi_rate', 'plan_duration_weeks',
            'amount', 'max_return', 'total_credited', 'remaining_return', 'progress_percent',
            'status', 'deposit_network', 'deposit_txn_hash', 'deposit_sender_address',
            'deposit_proof', 'deposit_proof_url', 'deposit_submitted_at', 'explorer_url',
            'approved_by_email', 'approved_at', 'rejection_reason',
            'start_date', 'end_date', 'last_roi_date', 'created_at', 'updated_at',
        ]

    def get_user_parent_email(self, obj) -> str | None:
        return obj.user.parent.email if obj.user.parent else None

    def get_progress_percent(self, obj) -> float:
        if obj.max_return and obj.max_return > 0:
            return round(min(100.0, float((obj.total_credited / obj.max_return) * 100)), 1)
        return 0.0

    def get_approved_by_email(self, obj) -> str | None:
        return obj.approved_by.email if obj.approved_by else None

    def get_deposit_proof_url(self, obj) -> str | None:
        if obj.deposit_proof:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.deposit_proof.url)
            return obj.deposit_proof.url
        return None

    def get_explorer_url(self, obj) -> str | None:
        if not obj.deposit_txn_hash:
            return None
        h = obj.deposit_txn_hash.strip()
        if (obj.deposit_network or '').upper() == 'TRC20' or not h.startswith('0x'):
            return f"https://tronscan.org/#/transaction/{h}"
        return f"https://bscscan.com/tx/{h}"


class AdminWithdrawalSerializer(serializers.ModelSerializer):
    """Admin view for withdrawals."""
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    user_wallet_balance = serializers.SerializerMethodField()
    reviewed_by_email = serializers.SerializerMethodField()
    rejection_reason = serializers.CharField(source='notes', read_only=True)
    explorer_url = serializers.SerializerMethodField()

    class Meta:
        model = Withdrawal
        fields = [
            'id', 'user_id', 'user_email', 'user_username', 'user_full_name', 'user_wallet_balance',
            'withdrawal_type', 'amount', 'fee', 'capital_charge', 'net_amount',
            'network', 'wallet_address', 'status', 'txn_hash', 'explorer_url',
            'reviewed_by_email', 'reviewed_at', 'notes', 'rejection_reason',
            'created_at', 'updated_at',
        ]

    def get_user_wallet_balance(self, obj) -> float:
        wallet = getattr(obj.user, 'wallet', None)
        return float(wallet.balance) if wallet else 0.0

    def get_reviewed_by_email(self, obj) -> str | None:
        return obj.reviewed_by.email if obj.reviewed_by else None

    def get_explorer_url(self, obj) -> str | None:
        if not obj.txn_hash:
            return None
        h = obj.txn_hash.strip()
        if (obj.network or '').upper() == 'TRC20' or not h.startswith('0x'):
            return f"https://tronscan.org/#/transaction/{h}"
        return f"https://bscscan.com/tx/{h}"


class AdminTicketReplySerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    is_staff = serializers.BooleanField(source='user.is_staff', read_only=True)

    class Meta:
        model = TicketReply
        fields = [
            'id', 'ticket_id', 'user_id', 'user_email', 'user_full_name',
            'is_staff', 'message', 'created_at',
        ]


class AdminTicketSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    replies = AdminTicketReplySerializer(many=True, read_only=True)
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'user_id', 'user_email', 'user_username',
            'subject', 'status', 'replies_count', 'replies',
            'created_at', 'updated_at',
        ]

    def get_replies_count(self, obj) -> int:
        return obj.replies.count()


class AdminPlatformSettingSerializer(serializers.ModelSerializer):
    updated_by_email = serializers.SerializerMethodField()

    class Meta:
        model = PlatformSettings
        fields = ['id', 'key', 'value', 'description', 'updated_at', 'updated_by_email']
        read_only_fields = ['id', 'updated_at', 'updated_by_email']

    def get_updated_by_email(self, obj) -> str | None:
        return obj.updated_by.email if obj.updated_by else None


class AdminPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            'id', 'name', 'description', 'minimum_amount', 'maximum_amount',
            'max_total_return', 'weekly_roi_rate', 'duration_weeks', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
