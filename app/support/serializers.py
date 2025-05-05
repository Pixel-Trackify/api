from rest_framework import serializers
from .models import Support, SupportReplyAttachment, SupportReply
import re


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
        """
        Valida o campo `title` para evitar scripts maliciosos e limitar a 100 caracteres.
        """
        if len(value) > 100:
            raise serializers.ValidationError(
                "O título não pode ter mais de 100 caracteres.")
        if not re.match(r'^[a-zA-Z0-9\s\-_,\.;:()áéíóúãõâêîôûçÁÉÍÓÚÃÕÂÊÎÔÛÇ]+$', value):
            raise serializers.ValidationError(
                "O título contém caracteres inválidos.")
        return value

    def validate_description(self, value):
        """
        Valida o campo `description` para evitar scripts maliciosos.
        """
        if not re.match(r'^[a-zA-Z0-9\s\-_,\.;:()áéíóúãõâêîôûçÁÉÍÓÚÃÕÂÊÎÔÛÇ]+$', value):
            raise serializers.ValidationError(
                "A descrição contém caracteres inválidos.")
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
