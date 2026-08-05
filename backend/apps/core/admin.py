from django.contrib import admin
from .models import PlatformSettings, AuditLog

@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'description', 'updated_at')
    search_fields = ('key', 'description')
    ordering = ('key',)
    readonly_fields = ('id', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return self.readonly_fields + ('key',)
        return self.readonly_fields

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'action', 'ip_address', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('user__email', 'ip_address')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'user', 'action', 'ip_address', 'user_agent', 'old_value', 'new_value', 'extra_data', 'created_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
