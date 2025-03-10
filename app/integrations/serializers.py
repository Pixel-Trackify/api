from rest_framework import serializers
from .models import Integration, Transaction, IntegrationRequest


class IntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Integration
        fields = ['id', 'uid', 'user', 'name', 'gateway',
                  'deleted', 'status', 'created_at', 'updated_at']


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
