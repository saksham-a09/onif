from rest_framework import serializers
from .models import Ticket, TicketReply


class TicketReplySerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    is_staff_reply = serializers.SerializerMethodField()

    class Meta:
        model = TicketReply
        fields = ['id', 'user_email', 'is_staff_reply', 'message', 'attachment', 'created_at']
        read_only_fields = ['id', 'user_email', 'is_staff_reply', 'created_at']

    def get_is_staff_reply(self, obj) -> bool:
        return obj.user.is_staff


class TicketSerializer(serializers.ModelSerializer):
    replies = TicketReplySerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'subject', 'status', 'replies', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'replies', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        ticket = super().create(validated_data)
        message = self.initial_data.get('message')
        if message:
            TicketReply.objects.create(ticket=ticket, user=validated_data['user'], message=message)
        return ticket


class TicketListSerializer(serializers.ModelSerializer):
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ['id', 'subject', 'status', 'reply_count', 'created_at', 'updated_at']

    def get_reply_count(self, obj) -> int:
        return obj.replies.count()


class TicketReplyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketReply
        fields = ['message', 'attachment']
