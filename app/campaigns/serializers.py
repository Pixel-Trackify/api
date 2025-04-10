from rest_framework import serializers
from collections import Counter
from integrations.models import IntegrationRequest
from .models import Campaign, CampaignView, Integration
import logging
from django.urls import reverse
from django.db.models import Sum
from datetime import datetime, timedelta
from django.utils import timezone

logger = logging.getLogger('django')


class CampaignSerializer(serializers.ModelSerializer):
    integrations = serializers.SlugRelatedField(
        slug_field='uid',
        queryset=Integration.objects.all(),
        many=True,
        error_messages={
            'does_not_exist': "Integração não foi encontrada.",
            'invalid': "Valor inválido."
        }
    )
    # Campo personalizado para estatísticas
    stats = serializers.SerializerMethodField()
    overviews = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            'id', 'uid', 'integrations', 'user', 'source', 'title', 'CPM', 'CPC', 'CPV', 'method',
            'total_approved', 'total_pending', 'amount_approved', 'amount_pending', 'total_abandoned', 'amount_abandoned', 'total_canceled', 'amount_canceled', 'total_refunded', 'amount_refunded', 'total_rejected', 'amount_rejected', 'total_chargeback', 'amount_chargeback',
            'total_ads', 'profit', 'ROI', 'total_views', 'total_clicks',
            'created_at', 'updated_at', 'stats', 'overviews'
        ]
        read_only_fields = ['id', 'uid', 'user', 'created_at', 'updated_at']

    def get_stats(self, obj):
        """
        Calcula as estatísticas de métodos de pagamento (payment_method)
        com base nas IntegrationRequests associadas à campanha.
        """
        # Obtém todas as integrações associadas à campanha
        integrations = obj.integrations.all()

        # Obtém todas as IntegrationRequests associadas às integrações
        integration_requests = IntegrationRequest.objects.filter(
            integration__in=integrations
        )

        # Conta os métodos de pagamento
        payment_methods = integration_requests.values_list(
            'payment_method', flat=True)
        stats = Counter(payment_methods)

        # Retorna as estatísticas no formato solicitado
        return stats

    def get_overviews(self, obj):
        today = timezone.now().date()  # Use timezone-aware datetime
        start_date = today - timedelta(days=30)

        # Obter despesas diárias (EXPENSE)
        expenses = obj.finance_logs.filter(
            date__gte=start_date,
            date__lte=today
        ).values('date').annotate(
            total_expense=Sum('total_ads')
        )

        # Obter receitas diárias (REVENUE)
        integrations = obj.integrations.all()

        revenues = IntegrationRequest.objects.filter(
            integration__in=integrations,  # Filtrar pelas integrações relacionadas
            status='APPROVED',
            created_at__gte=timezone.make_aware(
                datetime.combine(start_date, datetime.min.time())),
            created_at__lte=timezone.make_aware(
                datetime.combine(today, datetime.max.time()))
        ).values('created_at').annotate(
            total_revenue=Sum('amount')
        )

        # Combinar despesas e receitas
        overviews = []
        for expense in expenses:
            if 'total_expense' in expense and 'date' in expense:
                overviews.append({
                    "type": "EXPENSE",
                    "value": expense['total_expense'],
                    "date": expense['date']
                })
        for revenue in revenues:
            if 'total_revenue' in revenue and 'created_at' in revenue:
                overviews.append({
                    "type": "REVENUE",
                    "value": revenue['total_revenue'],
                    "date": revenue['created_at'].date()
                })

        # Ordenar por data
        overviews.sort(key=lambda x: x['date'])
        return overviews

    def validate_CPM_CPC_CPV(self, data):
        """
        Valida que apenas o campo correspondente ao método escolhido é obrigatório
        e que o valor é maior que 0.
        """
        method = data.get('method')
        CPM = data.get('CPM')
        CPC = data.get('CPC')
        CPV = data.get('CPV')

        # Verifica se o campo correspondente ao método foi preenchido
        if method == 'CPM':
            if CPM is None:
                raise serializers.ValidationError(
                    {"CPM": "O campo CPM é obrigatório quando o método é 'CPM'."})
            if CPM <= 0:
                raise serializers.ValidationError(
                    {"CPM": "O CPM deve ser maior que 0."})
            if CPC is not None or CPV is not None:
                raise serializers.ValidationError(
                    {"detail": "Apenas o campo CPM deve ser preenchido quando o método é 'CPM'."})

        elif method == 'CPC':
            if CPC is None:
                raise serializers.ValidationError(
                    {"CPC": "O campo CPC é obrigatório quando o método é 'CPC'."})
            if CPC <= 0:
                raise serializers.ValidationError(
                    {"CPC": "O CPC deve ser maior que 0."})
            if CPM is not None or CPV is not None:
                raise serializers.ValidationError(
                    {"detail": "Apenas o campo CPC deve ser preenchido quando o método é 'CPC'."})

        elif method == 'CPV':
            if CPV is None:
                raise serializers.ValidationError(
                    {"CPV": "O campo CPV é obrigatório quando o método é 'CPV'."})
            if CPV <= 0:
                raise serializers.ValidationError(
                    {"CPV": "O CPV deve ser maior que 0."})
            if CPM is not None or CPC is not None:
                raise serializers.ValidationError(
                    {"detail": "Apenas o campo CPV deve ser preenchido quando o método é 'CPV'."})

        return data

    def validate_integrations(self, value):
        """Valida se as integrações estão disponíveis ou já associadas à campanha"""

        instance = self.instance

        for integration in value:

            if instance and integration in instance.integrations.all():
                continue

            if integration.in_use:
                raise serializers.ValidationError(
                    f"O gateway '{integration.name}' já está em uso."
                )
        return value

    def create(self, validated_data):
        """Cria uma campanha e associa as integrações"""
        integrations = validated_data.pop('integrations', [])
        campaign = Campaign.objects.create(**validated_data)
        campaign.integrations.set(integrations)

        # Atualiza o campo `in_use` das integrações associadas
        for integration in integrations:
            integration.in_use = True
            integration.save()

        return campaign

    def update(self, instance, validated_data):
        """Atualiza uma campanha e associa as integrações, desativando as integrações removidas."""
        integrations = validated_data.pop('integrations', None)
        if integrations is not None:

            current_integrations = set(instance.integrations.all())
            new_integrations = set(integrations)
            removed_integrations = current_integrations - new_integrations

            for integration in removed_integrations:
                integration.in_use = False
                integration.save()

            for integration in new_integrations:
                integration.in_use = True
                integration.save()

            instance.integrations.set(integrations)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance


class CampaignViewSerializer(serializers.ModelSerializer):
    campaign = serializers.SlugRelatedField(
        slug_field='uid',
        queryset=Campaign.objects.all()
    )

    class Meta:
        model = CampaignView
        fields = ['id', 'campaign', 'user_agent',
                  'ip_address', 'action', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class PaginationMetadataSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = serializers.ListField(child=serializers.DictField(), default=[])
