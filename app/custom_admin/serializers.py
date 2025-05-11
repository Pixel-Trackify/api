from rest_framework import serializers
from accounts.models import Usuario
from campaigns.models import FinanceLogs
from custom_admin.models import Configuration


class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuration
        exclude = ['id']


class CaptchaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuration
        fields = ['recaptchar_enable', 'recaptchar_site_key']


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
    amount_approved = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_pending = serializers.IntegerField()
    amount_pending = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_refunded = serializers.IntegerField()
    amount_refunded = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_abandoned = serializers.IntegerField()
    amount_abandoned = serializers.DecimalField(
        max_digits=10, decimal_places=2)
    total_chargeback = serializers.IntegerField()
    amount_chargeback = serializers.DecimalField(
        max_digits=10, decimal_places=2)
    total_rejected = serializers.IntegerField()
    amount_rejected = serializers.DecimalField(max_digits=10, decimal_places=2)

    total_ads = serializers.IntegerField()
    profit = serializers.DecimalField(max_digits=10, decimal_places=2)

    total_views = serializers.IntegerField()
    total_clicks = serializers.IntegerField()
    stats = serializers.DictField()
    users = serializers.ListField()
    top_users = serializers.ListField()
