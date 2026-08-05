from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.support.models import Ticket, TicketReply

User = get_user_model()

class SupportModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='supportuser@example.com', username='supportuser')

    def test_ticket_creation(self):
        ticket = Ticket.objects.create(
            user=self.user,
            subject='Help with deposit'
        )
        self.assertEqual(ticket.status, Ticket.Status.OPEN)
        self.assertEqual(ticket.subject, 'Help with deposit')
        
        reply = TicketReply.objects.create(
            ticket=ticket,
            user=self.user,
            message='I sent the wrong screenshot.'
        )
        self.assertEqual(reply.ticket, ticket)
        self.assertEqual(reply.message, 'I sent the wrong screenshot.')
