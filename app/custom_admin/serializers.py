from rest_framework import serializers
from accounts.models import Usuario
from campaigns.models import FinanceLogs


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['uid', 'name', 'email', 'date_joined',
                  'profit', 'subscription_active']


class FinanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceLogs
        fields = ['user', 'date', 'amount',
                  'payment_method', 'views', 'clicks', 'stats']


class DashboardSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_users_subscription = serializers.IntegerField()
    total_approved = serializers.IntegerField()
    total_pending = serializers.IntegerField()
    amount_approved = serializers.DecimalField(max_digits=10, decimal_places=2)
    amount_pending = serializers.DecimalField(max_digits=10, decimal_places=2)
    profit = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_views = serializers.IntegerField()
    total_clicks = serializers.IntegerField()
    stats = serializers.DictField()
    users = serializers.ListField()
    top_users = serializers.ListField()
