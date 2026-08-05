from django.contrib import admin
from .models import Ticket, TicketReply

class TicketReplyInline(admin.StackedInline):
    model = TicketReply
    extra = 1
    readonly_fields = ('id', 'created_at')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'user', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'user__email', 'id')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [TicketReplyInline]
    
    actions = ['mark_as_resolved', 'mark_as_closed']
    
    @admin.action(description='Mark selected tickets as resolved')
    def mark_as_resolved(self, request, queryset):
        queryset.update(status=Ticket.Status.RESOLVED)
        
    @admin.action(description='Mark selected tickets as closed')
    def mark_as_closed(self, request, queryset):
        queryset.update(status=Ticket.Status.CLOSED)

@admin.register(TicketReply)
class TicketReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'user', 'created_at')
    search_fields = ('ticket__id', 'user__email', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at')
