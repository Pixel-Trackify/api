from rest_framework import serializers
from .models import Support, SupportReplyAttachment, SupportReply
import re
import html
from django.utils.html import strip_tags


class SupportSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = Support
        fields = ['uid', 'title', 'description',
                  'created_at', 'updated_at', 'files', 'role', 'closed', 'admin_read', 'user_read']

    def get_files(self, obj):
        return [attachment.file for attachment in obj.attachments.all()]

    def get_role(self, obj):
        if obj.user.is_superuser:
            return "admin"
        return "user"

    def validate_title(self, value):
        try:
            value.encode('latin-1')
        except UnicodeEncodeError:
            raise serializers.ValidationError(
                "O campo só pode conter caracteres ASCII.")

        if html.unescape(strip_tags(value)) != value:
            raise serializers.ValidationError(
                "O campo não pode conter tags HTML.")

        if len(value) < 5:
            raise serializers.ValidationError(
                "O campo deve ter pelo menos 5 caracteres.")

        if len(value) > 100:
            raise serializers.ValidationError(
                "O campo não pode exceder 100 caracteres.")

        return value

    def validate_description(self, value):
        if not value:
            return value

        try:
            value.encode('latin-1')
        except UnicodeEncodeError:
            raise serializers.ValidationError(
                "O campo só pode conter caracteres ASCII.")

        if html.unescape(strip_tags(value)) != value:
            raise serializers.ValidationError(
                "O campo não pode conter tags HTML.")

        if len(value) < 5:
            raise serializers.ValidationError(
                "O campo deve ter pelo menos 5 caracteres.")

        if len(value) > 500:
            raise serializers.ValidationError(
                "O campo não pode exceder 500 caracteres.")

        return value


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
