from django.contrib import admin
from .models import Wallet, WalletTransaction

class WalletTransactionInline(admin.TabularInline):
    model = WalletTransaction
    extra = 0
    readonly_fields = ('transaction_type', 'category', 'amount', 'balance_before', 'balance_after', 'reference_id', 'created_at')
    can_delete = False
    ordering = ('-created_at',)
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'total_deposited', 'total_roi_earned', 'total_direct_income', 'total_referral_income', 'updated_at')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [WalletTransactionInline]

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet', 'transaction_type', 'category', 'amount', 'created_at')
    list_filter = ('transaction_type', 'category', 'created_at')
    search_fields = ('wallet__user__email', 'reference_id')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at')
