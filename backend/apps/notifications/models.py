import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    """
    In-app notification for a user or broadcast to all users.

    If `user` is null and `is_broadcast` is True, the notification is
    an admin announcement visible to all users.
    """

    class NotificationType(models.TextChoices):
        SYSTEM = 'SYSTEM', _('System')
        INVESTMENT = 'INVESTMENT', _('Investment')
        DEPOSIT = 'DEPOSIT', _('Deposit')
        WITHDRAWAL = 'WITHDRAWAL', _('Withdrawal')
        REFERRAL = 'REFERRAL', _('Referral')
        ANNOUNCEMENT = 'ANNOUNCEMENT', _('Announcement')
        KYC = 'KYC', _('KYC')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name=_('User'),
        help_text=_('Null for broadcast notifications'),
    )
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    message = models.TextField(verbose_name=_('Message'))
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
        db_index=True,
        verbose_name=_('Type'),
    )
    is_read = models.BooleanField(default=False, db_index=True, verbose_name=_('Is Read'))
    is_broadcast = models.BooleanField(
        default=False, db_index=True, verbose_name=_('Is Broadcast')
    )
    reference_id = models.CharField(
        max_length=100, blank=True, verbose_name=_('Reference ID'),
        help_text=_('UUID of the related object for deep-linking'),
    )

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self) -> str:
        target = self.user or 'ALL'
        return f"[{self.notification_type}] {self.title} → {target}"
