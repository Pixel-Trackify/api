from rest_framework import serializers
from .models import Integration, Transaction, IntegrationRequest
from django.conf import settings
import logging
from django.utils.html import strip_tags
import html


logger = logging.getLogger('django')


class IntegrationSerializer(serializers.ModelSerializer):
    webhook_url = serializers.SerializerMethodField()

    class Meta:
        model = Integration
        fields = ['id', 'uid', 'user', 'name', 'gateway',
                  'deleted', 'status', 'created_at', 'updated_at', 'webhook_url', 'in_use']
        read_only_fields = ['id', 'uid', 'user', 'deleted',
                            'status', 'created_at', 'updated_at']

    def validate_name(self, value):
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

    def validate_gateway(self, value):
        """
        Valida o campo `gateway` para aceitar tanto o `id` quanto o `name` dos `choices`.
        """
        valid_gateways = Integration._meta.get_field('gateway').choices
        gateway_mapping = {choice[1]: choice[0]
                           for choice in valid_gateways}  # Mapeia name -> id
        gateway_mapping.update(
            # Adiciona id -> id
            {choice[0]: choice[0] for choice in valid_gateways})

        if value not in gateway_mapping:
            raise serializers.ValidationError(
                f"Gateway inválido. Escolha um dos seguintes: {', '.join(gateway_mapping.keys())}"
            )

        # Converte o valor (name ou id) para o formato do banco de dados (id)
        return gateway_mapping[value]

    def get_webhook_url(self, obj):
        """
        Gera a URL do webhook com base no domínio configurado no .env, gateway e UID da integração.
        """
        base_url = settings.WEBHOOK_BASE_URL  # Obtém o domínio do .env
        return f"{base_url}{obj.gateway.lower()}/{obj.uid}/"


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'uid', 'integration', 'transaction_id', 'method',
                  'amount', 'status', 'data_response', 'created_at', 'updated_at']


class IntegrationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationRequest
        fields = ['id', 'uid', 'integration', 'status', 'payment_id', 'payment_method',
                  'amount', 'phone', 'name', 'email', 'response', 'created_at', 'updated_at']
        read_only_fields = ['integration', 'status', 'payment_id',
                            'payment_method', 'amount', 'response', 'created_at', 'updated_at']


class DeleteMultipleSerializer(serializers.Serializer):
    uids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="Lista de UUIDs das integrações a serem excluídas."
    )
