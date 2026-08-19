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


from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

class SupportViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='viewsupport@example.com', username='viewsupport')
        self.client.force_authenticate(user=self.user)
        self.ticket = Ticket.objects.create(user=self.user, subject='Need help with login')

    def test_list_tickets(self):
        url = reverse('ticket_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_ticket(self):
        url = reverse('ticket_list_create')
        data = {'subject': 'Another issue', 'message': 'Please help me.'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['subject'], 'Another issue')
        self.assertEqual(Ticket.objects.count(), 2)

    def test_reply_to_ticket(self):
        url = reverse('ticket_reply', kwargs={'pk': self.ticket.id})
        data = {'message': 'Just following up.'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_reply_to_closed_ticket_fails(self):
        self.ticket.status = Ticket.Status.CLOSED
        self.ticket.save()
        url = reverse('ticket_reply', kwargs={'pk': self.ticket.id})
        data = {'message': 'Trying to reply.'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reply_reopens_resolved_ticket(self):
        self.ticket.status = Ticket.Status.RESOLVED
        self.ticket.save()
        url = reverse('ticket_reply', kwargs={'pk': self.ticket.id})
        data = {'message': 'Actually, not resolved yet.'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.OPEN)
