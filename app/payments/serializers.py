from rest_framework import serializers
from .models import Subscription, SubscriptionPayment


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'uid', 'plan', 'user', 'status', 'expiration']


class SubscriptionPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPayment
        fields = ['id', 'uid', 'idempotency', 'payment_method', 'token',
                  'price', 'gateway_response', 'status', 'subscription', 'user']
