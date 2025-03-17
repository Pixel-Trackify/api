from rest_framework import serializers
from .models import Campaign, CampaignView, Integration


class CampaignSerializer(serializers.ModelSerializer):
    integrations = serializers.ListField(
        child=serializers.UUIDField(), write_only=True
    )

    class Meta:
        model = Campaign
        fields = ['id', 'title', 'CPM', 'integrations']

    def create(self, validated_data):
        user = validated_data.pop('user')
        integrations_uids = validated_data.pop('integrations', [])
        integrations = Integration.objects.filter(uid__in=integrations_uids)
        campaign = Campaign.objects.create(user=user, **validated_data)
        campaign.integrations.set(integrations)
        return campaign

    def update(self, instance, validated_data):
        integrations_uids = validated_data.pop('integrations', [])
        integrations = Integration.objects.filter(uid__in=integrations_uids)
        instance.integrations.set(integrations)
        return super().update(instance, validated_data)


class CampaignViewSerializer(serializers.ModelSerializer):
    campaign = serializers.SlugRelatedField(
        slug_field='uid',
        queryset=Campaign.objects.all()
    )

    class Meta:
        model = CampaignView
        fields = '__all__'
