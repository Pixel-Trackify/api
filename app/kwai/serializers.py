from rest_framework import serializers
from campaigns.models import FinanceLogs


class FinanceLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceLogs
        exclude = ['id']
