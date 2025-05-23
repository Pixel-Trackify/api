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
        fields = ['uid', 'title', 'in_use',
                  'deleted']


class KwaiSerializer(serializers.ModelSerializer):

    campaigns = serializers.ListField(
        child=serializers.DictField(
            child=serializers.UUIDField(
                error_messages={'invalid': 'Must be a valid UUID.'})
        ),
        write_only=True,
        required=True
    )

    class Meta:
        model = Kwai
        fields = ['uid', 'name', 'user',
                  'campaigns',  'created_at', 'updated_at']
        read_only_fields = ['uid', 'user', 'created_at', 'updated_at']

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

    def validate_campaigns(self, value):
        """
        Valida o campo 'campaigns' para garantir que ele não esteja vazio.
        """
        if not value:
            raise serializers.ValidationError(
                "O campo é obrigatório."
            )
        return value

    def get_campaigns(self, obj):
        """
        Retorna as campanhas associadas a esta conta do Kwai, apenas as não deletadas.
        """
        campaigns = obj.campaigns.filter(deleted=False)
        return CampaignSerializer(campaigns, many=True).data

    def to_representation(self, instance):
        """
        Personaliza a representação dos dados para incluir os dados financeiros da campanha,
        filtrando por intervalo de datas se fornecido na request.
        """
        representation = super().to_representation(instance)

        # Adiciona as campanhas associadas (apenas não deletadas)
        campaigns = Campaign.objects.filter(
            kwai_campaigns__kwai=instance, deleted=False)
        representation["campaigns"] = CampaignSerializer(
            campaigns, many=True).data

        # Obtém os parâmetros de data da request, se existirem
        request = self.context.get('request')
        start_date = request.query_params.get('start') if request else None
        end_date = request.query_params.get('end') if request else None

        if start_date and end_date < start_date:
            raise serializers.ValidationError(
                {"start": "A data de início não pode ser maior que a data de fim."}
            )
        
        # Obtém os dados financeiros agregados filtrados por data
        financial_data = get_financial_data(
            kwai=instance, start_date=start_date, end_date=end_date)

        fields_to_remove = ['source', 'CPM', 'CPC', 'CPV', 'method']
        for field in fields_to_remove:
            financial_data.pop(field, None)

        representation.update(financial_data)

        return representation

    def create(self, validated_data):
        campaigns_data = validated_data.pop('campaigns')
        # Validação: Verificar se todas as campanhas existem e não estão em uso
        campaigns = []
        for campaign_data in campaigns_data:
            try:
                campaign = Campaign.objects.get(
                    uid=campaign_data['uid'], deleted=False)
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
            current_campaigns = set(
                Campaign.objects.filter(
                    kwai_campaigns__kwai=instance, deleted=False)
            )
            new_campaigns = set()
            campaigns = []

            for campaign_data in campaigns_data:
                uid = campaign_data.get('uid')

                try:
                    uuid.UUID(str(uid))
                except ValueError:
                    raise serializers.ValidationError(
                        {"campaigns": f"O valor '{uid}' não é um UUID válido."}
                    )

                try:
                    campaign = Campaign.objects.get(uid=uid, deleted=False)
                    if campaign.in_use and campaign not in current_campaigns:
                        raise serializers.ValidationError(
                            {"campaigns": f"A campanha '{campaign.uid}' já está em uso."}
                        )
                    campaigns.append(campaign)
                    new_campaigns.add(campaign)
                except Campaign.DoesNotExist:
                    raise serializers.ValidationError(
                        {"campaigns": f"A campanha com UID '{uid}' não existe ou está deletada."}
                    )

            removed_campaigns = current_campaigns - new_campaigns
            for campaign in removed_campaigns:
                campaign.in_use = False
                campaign.save()

            KwaiCampaign.objects.filter(kwai=instance).delete()

            for campaign in campaigns:
                campaign.in_use = True
                campaign.save()
                KwaiCampaign.objects.create(kwai=instance, campaign=campaign)

        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance
