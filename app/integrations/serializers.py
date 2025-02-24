from rest_framework import serializers
from .models import Integration, Transaction


class IntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Integration
        fields = ['id', 'name', 'uid', 'user']
        read_only_fields = ['id', 'uid', 'user']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
