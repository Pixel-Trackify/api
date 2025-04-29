from rest_framework import serializers
from .models import Kwai, KwaiCampaign
from campaigns.models import FinanceLogs, Campaign
import uuid
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta


class FinanceLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceLogs
        exclude = ['id']


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ['uid', 'title', 'in_use']


class KwaiSerializer(serializers.ModelSerializer):
    # Campo para leitura das campanhas associadas
    campaigns = serializers.SerializerMethodField()
    overviews = serializers.SerializerMethodField()

    class Meta:
        model = Kwai
        fields = ['uid', 'name', 'user',
                  'campaigns', 'created_at', 'updated_at', 'overviews']

    def get_campaigns(self, obj):
        """
        Retorna as campanhas associadas a esta conta do Kwai.
        """
        campaigns = Campaign.objects.filter(
            kwai_campaigns__kwai=obj)  # Obtém as campanhas associadas
        return CampaignSerializer(campaigns, many=True).data

    def get_overviews(self, obj):
        """
        Obtém os dados de despesas (EXPENSE) e receitas (REVENUE) diretamente da tabela FinanceLogs.
        """
        today = timezone.now().date()
        start_date = today - timedelta(days=30)

        # Obtém os registros de FinanceLogs associados à campanha no intervalo de 30 dias
        finance_logs = FinanceLogs.objects.filter(
            campaign__kwai_campaigns__kwai=obj,
            date__gte=start_date,
            date__lte=today
        )

        # Inicializa a lista de overviews
        overviews = []

        # Adiciona as despesas (EXPENSE) ao overview
        expenses = finance_logs.values('date').annotate(
            total_expense=Sum('total_ads'))
        for expense in expenses:
            if 'total_expense' in expense and 'date' in expense:
                overviews.append({
                    "type": "EXPENSE",
                    "value": expense['total_expense'],
                    "date": expense['date']
                })

        # Adiciona as receitas (REVENUE) ao overview
        revenues = finance_logs.values('date').annotate(
            total_revenue=Sum('amount_approved'))
        for revenue in revenues:
            if 'total_revenue' in revenue and 'date' in revenue:
                overviews.append({
                    "type": "REVENUE",
                    "value": revenue['total_revenue'],
                    "date": revenue['date']
                })

        # Ordena os resultados por data
        overviews.sort(key=lambda x: x['date'])

        return overviews

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
