from rest_framework import serializers
from .models import Support, SupportReplyAttachment, SupportReply


class SupportSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = Support
        fields = ['uid', 'title', 'description',
                  'created_at', 'updated_at', 'files', 'role']

    def get_files(self, obj):
        return [attachment.file for attachment in obj.attachments.all()]

    def get_role(self, obj):
        if obj.user.is_superuser:
            return "admin"
        return "user"


class SupportReplyAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportReplyAttachment
        exclude = ['id', 'support', 'support_reply']


class SupportReplySerializer(serializers.ModelSerializer):
    support_uid = serializers.CharField(source='support.uid', read_only=True)
    role = serializers.SerializerMethodField()

    class Meta:
        model = SupportReply
        fields = ['uid', 'support_uid', 'description',
                  'created_at', 'role']

    def get_role(self, obj):
        if obj.user.is_superuser:
            return "admin"
        return "user"
