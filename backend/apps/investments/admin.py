from django.contrib import admin
from django.utils import timezone
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
    
    @admin.action(description='Approve selected investments & distribute direct income')
    def approve_investments(self, request, queryset):
        from apps.investments.tasks import distribute_direct_income_task
        for investment in queryset.filter(status=Investment.Status.PENDING):
            investment.status = Investment.Status.ACTIVE
            investment.approved_by = request.user
            investment.approved_at = timezone.now()
            investment.start_date = timezone.now().date()
            investment.save(update_fields=['status', 'approved_by', 'approved_at', 'start_date'])
            # Trigger async direct income + notification
            distribute_direct_income_task.delay(str(investment.id))
        self.message_user(request, "Selected investments approved and income distribution queued.")
        
    @admin.action(description='Cancel selected investments')
    def cancel_investments(self, request, queryset):
        queryset.update(status=Investment.Status.CANCELLED)
