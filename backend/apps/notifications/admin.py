from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'notification_type', 'user', 'is_broadcast', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_broadcast', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at')
