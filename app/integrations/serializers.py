from rest_framework import serializers
from .models import Integration, Transaction, IntegrationRequest
from django.urls import reverse


class IntegrationSerializer(serializers.ModelSerializer):
    webhook_url = serializers.SerializerMethodField()

    class Meta:
        model = Integration
        fields = ['id', 'uid', 'user', 'name', 'gateway',
                  'deleted', 'status', 'created_at', 'updated_at', 'webhook_url']
        read_only_fields = ['id', 'uid', 'user', 'deleted',
                            'status', 'created_at', 'updated_at']

    def get_webhook_url(self, obj):
        """
        Gera a URL do webhook com base no gateway e no UID da integração.
        """
        request = self.context.get('request')
        if not request:
            return None
        return request.build_absolute_uri(
            reverse(
                f"{obj.gateway.lower()}-webhook",
                kwargs={"uid": obj.uid},
            )
        )


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
