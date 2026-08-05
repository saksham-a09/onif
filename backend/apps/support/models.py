import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

class Ticket(models.Model):
    """
    Customer Support Ticket
    """
    class Status(models.TextChoices):
        OPEN = 'OPEN', _('Open')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        RESOLVED = 'RESOLVED', _('Resolved')
        CLOSED = 'CLOSED', _('Closed')
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='tickets', 
        verbose_name=_('User')
    )
    subject = models.CharField(max_length=255, verbose_name=_('Subject'))
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.OPEN, 
        db_index=True, 
        verbose_name=_('Status')
    )
    
    class Meta:
        verbose_name = _('Ticket')
        verbose_name_plural = _('Tickets')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Ticket {self.id}: {self.subject} ({self.status})"

class TicketReply(models.Model):
    """
    Reply to a Customer Support Ticket
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    ticket = models.ForeignKey(
        Ticket, 
        on_delete=models.CASCADE, 
        related_name='replies', 
        verbose_name=_('Ticket')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='ticket_replies', 
        verbose_name=_('User')
    )
    message = models.TextField(verbose_name=_('Message'))
    attachment = models.FileField(
        upload_to='ticket_attachments/', 
        blank=True, 
        null=True, 
        verbose_name=_('Attachment')
    )
    
    class Meta:
        verbose_name = _('Ticket Reply')
        verbose_name_plural = _('Ticket Replies')
        ordering = ['created_at']
        
    def __str__(self):
        return f"Reply by {self.user} on Ticket {self.ticket.id}"
