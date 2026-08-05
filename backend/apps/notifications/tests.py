from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.notifications.models import Notification

User = get_user_model()


class NotificationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='notifuser@example.com', username='notifuser')

    def test_user_notification(self):
        notif = Notification.objects.create(
            user=self.user,
            title='Deposit Approved',
            message='Your deposit of $500 has been approved.',
            notification_type=Notification.NotificationType.DEPOSIT
        )
        self.assertFalse(notif.is_read)
        self.assertFalse(notif.is_broadcast)

    def test_broadcast_notification(self):
        notif = Notification.objects.create(
            title='System Maintenance',
            message='Scheduled maintenance on Saturday.',
            notification_type=Notification.NotificationType.ANNOUNCEMENT,
            is_broadcast=True
        )
        self.assertTrue(notif.is_broadcast)
        self.assertIsNone(notif.user)
