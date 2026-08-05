from django.contrib import admin
from .models import Plan, Investment

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'minimum_amount', 'maximum_amount', 'max_total_return', 'weekly_roi_rate', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('minimum_amount',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    
@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'plan', 'amount', 'status', 'total_credited', 'max_return', 'start_date', 'end_date')
    list_filter = ('status', 'plan', 'created_at')
    search_fields = ('user__email', 'user__username', 'id')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    actions = ['approve_investments', 'cancel_investments']
    
    @admin.action(description='Approve selected investments')
    def approve_investments(self, request, queryset):
        queryset.update(status=Investment.Status.ACTIVE)
        
    @admin.action(description='Cancel selected investments')
    def cancel_investments(self, request, queryset):
        queryset.update(status=Investment.Status.CANCELLED)
