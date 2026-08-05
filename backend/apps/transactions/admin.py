from django.contrib import admin
from .models import Deposit, Withdrawal

@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'network', 'status', 'txn_hash', 'created_at')
    list_filter = ('status', 'network', 'created_at')
    search_fields = ('user__email', 'txn_hash', 'id')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    actions = ['approve_deposits', 'reject_deposits']
    
    @admin.action(description='Approve selected deposits')
    def approve_deposits(self, request, queryset):
        queryset.update(status=Deposit.Status.APPROVED)
        
    @admin.action(description='Reject selected deposits')
    def reject_deposits(self, request, queryset):
        queryset.update(status=Deposit.Status.REJECTED)

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'withdrawal_type', 'amount', 'net_amount', 'network', 'status', 'created_at')
    list_filter = ('status', 'withdrawal_type', 'network', 'created_at')
    search_fields = ('user__email', 'wallet_address', 'txn_hash', 'id')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'net_amount')
    
    actions = ['approve_withdrawals', 'reject_withdrawals']
    
    @admin.action(description='Approve selected withdrawals')
    def approve_withdrawals(self, request, queryset):
        queryset.update(status=Withdrawal.Status.APPROVED)
        
    @admin.action(description='Reject selected withdrawals')
    def reject_withdrawals(self, request, queryset):
        queryset.update(status=Withdrawal.Status.REJECTED)
