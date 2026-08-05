from django.contrib import admin
from .models import ReferralRelationship, ReferralCommission

@admin.register(ReferralRelationship)
class ReferralRelationshipAdmin(admin.ModelAdmin):
    list_display = ('user', 'sponsor', 'created_at')
    search_fields = ('user__email', 'sponsor__email')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at')

@admin.register(ReferralCommission)
class ReferralCommissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'from_user', 'commission_type', 'level', 'amount', 'is_paid', 'created_at')
    list_filter = ('commission_type', 'level', 'is_paid', 'created_at')
    search_fields = ('user__email', 'from_user__email')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    actions = ['mark_as_paid']
    
    @admin.action(description='Mark selected commissions as paid')
    def mark_as_paid(self, request, queryset):
        queryset.update(is_paid=True)
