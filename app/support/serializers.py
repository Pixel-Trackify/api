from rest_framework import serializers
from .models import Support, SupportReplyAttachment, SupportReply


class SupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Support
        fields = ['title', 'replies', 'description',
                  'created_at', 'updated_at']


class SupportReplyAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportReplyAttachment
        # Exclui os campos id e relações
        exclude = ['id', 'support', 'support_reply']


class SupportReplySerializer(serializers.ModelSerializer):
    attachments = SupportReplyAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = SupportReply
        exclude = ['id', 'user', 'role']  # Exclui os campos id e user
