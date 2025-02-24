from rest_framework import serializers
from .models import Campaign, CampaignView

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'

class CampaignViewSerializer(serializers.ModelSerializer):
    campaign = serializers.SlugRelatedField(
        slug_field='uid',
        queryset=Campaign.objects.all()
    )

    class Meta:
        model = CampaignView
        fields = '__all__'