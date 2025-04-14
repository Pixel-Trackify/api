from rest_framework import serializers
from .models import Support, SupportReplyAttachment, SupportReply


class SupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Support
        fields = ['title', 'replies', 'description',
                  'created_at', 'updated_at', 'status', 'uid']


class SupportReplyAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportReplyAttachment
        # Exclui os campos id e relações
        fields = ['attachment', 'created_at',
                  'updated_at', 'support_reply', 'uid']
        exclude = ['id']


class SupportReplySerializer(serializers.ModelSerializer):
    attachments = SupportReplyAttachmentSerializer(many=True, read_only=True)

    class Meta:
        fields = ['uid', 'reply', 'created_at', 'updated_at',
                  'support', 'user', 'role', 'attachments']
        model = SupportReply
        exclude = ['id']  # Exclui os campos id e user
