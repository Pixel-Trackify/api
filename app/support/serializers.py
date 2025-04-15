from rest_framework import serializers
from .models import Support, SupportReplyAttachment, SupportReply


class SupportSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()

    class Meta:
        model = Support
        fields = ['uid', 'title', 'description',
                  'created_at', 'updated_at', 'files']

    def get_files(self, obj):
        return [attachment.file for attachment in obj.attachments.all()]


class SupportReplyAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportReplyAttachment
        # Exclui os campos id e relações
        exclude = ['id', 'support', 'support_reply']


class SupportReplySerializer(serializers.ModelSerializer):
    support_uid = serializers.CharField(source='support.uid', read_only=True)

    class Meta:
        model = SupportReply
        fields = ['uid', 'support_uid', 'description',
                  'created_at']
