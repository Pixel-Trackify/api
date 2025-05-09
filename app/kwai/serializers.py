from rest_framework import serializers
from .models import Kwai, KwaiCampaign
from campaigns.models import FinanceLogs, Campaign
import uuid
from .services import get_financial_data
from django.utils.html import strip_tags
import html


class FinanceLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceLogs
        exclude = ['id']


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ['uid', 'title', 'in_use']


class KwaiSerializer(serializers.ModelSerializer):

    campaigns = serializers.SerializerMethodField()

    class Meta:
        model = Kwai
        fields = ['uid', 'name', 'user',
                  'campaigns', 'created_at', 'updated_at']

    def validate_name(self, value):
        try:
            value.encode('latin-1')
        except UnicodeEncodeError:
            raise serializers.ValidationError(
                "O campo só pode conter caracteres ASCII.")

        if html.unescape(strip_tags(value)) != value:
            raise serializers.ValidationError(
                "O campo não pode conter tags HTML.")

        if len(value) < 5:
            raise serializers.ValidationError(
                "O campo deve ter pelo menos 5 caracteres.")

        if len(value) > 100:
            raise serializers.ValidationError(
                "O campo não pode exceder 100 caracteres.")

        return value

    def get_campaigns(self, obj):
        """
        Retorna as campanhas associadas a esta conta do Kwai.
        """
        campaigns = Campaign.objects.filter(
            kwai_campaigns__kwai=obj)  # Obtém as campanhas associadas
        return CampaignSerializer(campaigns, many=True).data

    def to_representation(self, instance):
        """
        Personaliza a representação dos dados para incluir os dados financeiros da campanha.
        """
        # Obtém a representação padrão
        representation = super().to_representation(instance)

        # Obtém os dados financeiros agregados
        financial_data = get_financial_data(kwai=instance)

        fields_to_remove = ['source', 'CPM', 'CPC', 'CPV', 'method']
        for field in fields_to_remove:
            financial_data.pop(field, None)

        # Combina os dados financeiros com os dados da conta Kwai
        representation.update(financial_data)

        return representation

    def create(self, validated_data):
        request = self.context.get('request')
        campaigns_data = request.data.get('campaigns', None)

        if not campaigns_data:
            raise serializers.ValidationError(
                {"campaigns": "O campo 'campaigns' é obrigatório e não pode estar vazio."}
            )

        # Validação: Verificar se todas as campanhas existem e não estão em uso
        campaigns = []
        for campaign_data in campaigns_data:
            try:
                campaign = Campaign.objects.get(uid=campaign_data['uid'])
                if campaign.in_use:
                    raise serializers.ValidationError(
                        {"campaigns": f"A campanha já está em uso."}
                    )
                campaigns.append(campaign)
            except Campaign.DoesNotExist:
                raise serializers.ValidationError(
                    {"campaigns":
                        f"A campanha com UID não existe."}
                )

        kwai = Kwai.objects.create(**validated_data)

        for campaign in campaigns:
            campaign.in_use = True
            campaign.save()
            KwaiCampaign.objects.create(kwai=kwai, campaign=campaign)

        return kwai

    def update(self, instance, validated_data):

        campaigns_data = validated_data.pop('campaigns', None)

        if campaigns_data:

            KwaiCampaign.objects.filter(kwai=instance).delete()

            campaigns = []
            for campaign_data in campaigns_data:
                uid = campaign_data.get('uid')

                try:
                    uuid.UUID(uid)
                except ValueError:
                    raise serializers.ValidationError(
                        {"campaigns": f"O valor '{uid}' não é um UUID válido."}
                    )

                try:
                    campaign = Campaign.objects.get(uid=uid)
                    if campaign.in_use and campaign not in instance.campaigns.all():
                        raise serializers.ValidationError(
                            {"campaigns": f"A campanha '{campaign.uid}' já está em uso."}
                        )
                    campaigns.append(campaign)
                except Campaign.DoesNotExist:
                    raise serializers.ValidationError(
                        {"campaigns": f"A campanha com UID '{uid}' não existe."}
                    )

            for campaign in campaigns:
                campaign.in_use = True
                campaign.save()
                KwaiCampaign.objects.create(kwai=instance, campaign=campaign)

        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance
