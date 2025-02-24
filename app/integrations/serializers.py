from rest_framework import serializers
from .models import Integration, Transaction

class IntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Integration
        fields = ['id', 'uid', 'user', 'name', 'platform', 'credentials']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'uid', 'integration', 'transaction_id', 'method', 'amount', 'status', 'data_response', 'created_at', 'updated_at']