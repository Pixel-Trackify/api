from rest_framework import serializers
from .models import Campaign, CampaignView


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'


class CampaignViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignView
        fields = '__all__'
