from rest_framework import serializers
from collections import Counter
from integrations.models import IntegrationRequest
from .models import Campaign, CampaignView, Integration
import logging
from django.db.models import Sum
from datetime import timedelta
from django.utils import timezone
from django.utils.html import strip_tags
import html

logger = logging.getLogger('django')


class CampaignSerializer(serializers.ModelSerializer):
    integrations = serializers.SlugRelatedField(
        slug_field='uid',
        queryset=Integration.objects.filter(deleted=False),
        many=True,
        required=True,
        error_messages={
            'does_not_exist': "Integração não foi encontrada.",
            'invalid': "Valor inválido."
        }
    )
    method = serializers.ChoiceField(
        choices=Campaign.METHOD_CHOICES,
        required=True,
        error_messages={'required': 'Este campo é obrigatório.'}
    )
    # Campo personalizado para estatísticas
    stats = serializers.SerializerMethodField()
    overviews = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            'uid', 'integrations', 'user', 'source', 'title', 'description', 'CPM', 'CPC', 'CPV', 'method',
            'total_approved', 'total_pending', 'amount_approved', 'amount_pending', 'total_abandoned', 'amount_abandoned', 'total_canceled', 'amount_canceled', 'total_refunded', 'amount_refunded', 'total_rejected', 'amount_rejected', 'total_chargeback', 'amount_chargeback',
            'total_ads', 'profit', 'ROI', 'total_views', 'total_clicks',
            'created_at', 'updated_at', 'stats', 'overviews'
        ]
        read_only_fields = ['id', 'uid', 'user', 'created_at', 'updated_at']

    def validate_CPM(self, value):
        method = self.initial_data.get('method')
        # Se vier um valor de CPM mas o método não for CPM
        if method != 'CPM':
            raise serializers.ValidationError(
                "Este campo é obrigatório."
            )

        if value is None:
            raise serializers.ValidationError(
                "Este campo é obrigatório."
            )

        if value <= 0:
            raise serializers.ValidationError(
                "Este campo deve ser maior que zero."
            )

        # CPM precisa ser > 0
        if value is None or value <= 0:
            raise serializers.ValidationError(
                "Este campo deve ser maior que zero."
            )
        return value

    def validate_CPC(self, value):
        method = self.initial_data.get('method')
        if method != 'CPC':
            raise serializers.ValidationError(
                "Este campo é obrigatório."
            )

        if value is None:
            raise serializers.ValidationError(
                "Este campo é obrigatório."
            )

        if value <= 0:
            raise serializers.ValidationError(
                "Este campo deve ser maior que zero."
            )

        if value is None or value <= 0:
            raise serializers.ValidationError(
                "Este campo deve ser maior que zero."
            )
        return value

    def validate_CPV(self, value):
        method = self.initial_data.get('method')
        if method != 'CPV':
            raise serializers.ValidationError(
                "Este campo é obrigatório."
            )

        if value is None:
            raise serializers.ValidationError(
                "Este campo é obrigatório."
            )

        if value <= 0:
            raise serializers.ValidationError(
                "Este campo deve ser maior que zero."
            )

        if value is None or value <= 0:
            raise serializers.ValidationError(
                "Este campo deve ser maior que zero."
            )
        return value

    def get_stats(self, obj):

        stats = obj.finance_logs.aggregate(
            credit_card_amount=Sum('credit_card_amount'),
            debit_card_amount=Sum('debit_card_amount'),
            pix_amount=Sum('pix_amount'),
            boleto_amount=Sum('boleto_amount')
        )

        return {
            "CREDIT_CARD": stats.get('credit_card_amount', 0) or 0,
            "DEBIT_CARD": stats.get('debit_card_amount', 0) or 0,
            "PIX": stats.get('pix_amount', 0) or 0,
            "BOLETO": stats.get('boleto_amount', 0) or 0,
        }

    def get_overviews(self, obj):
        """
        Obtém os dados de despesas (EXPENSE) e receitas (REVENUE) diretamente da tabela FinanceLogs.
        """
        today = timezone.now().date()
        start_date = today - timedelta(days=30)

        # Obtém os registros de FinanceLogs associados à campanha no intervalo de 30 dias
        finance_logs = obj.finance_logs.filter(
            date__gte=start_date, date__lte=today)

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

    def validate_title(self, value):
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

    def validate_description(self, value):
        if not value:
            return value

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

        if len(value) > 500:
            raise serializers.ValidationError(
                "O campo não pode exceder 500 caracteres.")

        return value

    def validate_integrations(self, value):
        """Valida se as integrações estão disponíveis ou já associadas à campanha"""

        instance = self.instance

        for integration in value:

            if instance and integration in instance.integrations.all():
                continue

            if integration.in_use:
                raise serializers.ValidationError(
                    f"A Integração '{integration.name}' já está em uso."
                )
        return value

    def validate(self, attrs):
        integrations = attrs.get(
            'integrations') or self.initial_data.get('integrations')
        if not integrations:
            raise serializers.ValidationError(
                {"integrations": "Selecione pelo menos uma integração."}
            )

        method = attrs.get('method') or self.initial_data.get('method')
        if method == 'CPM' and (attrs.get('CPM') is None or attrs.get('CPM', 0) <= 0):
            raise serializers.ValidationError(
                {"CPM": "Este campo é obrigatório e deve ser maior que zero."})
        if method == 'CPC' and (attrs.get('CPC') is None or attrs.get('CPC', 0) <= 0):
            raise serializers.ValidationError(
                {"CPC": "Este campo é obrigatório e deve ser maior que zero."})
        if method == 'CPV' and (attrs.get('CPV') is None or attrs.get('CPV', 0) <= 0):
            raise serializers.ValidationError(
                {"CPV": "Este campo é obrigatório e deve ser maior que zero."})
        return attrs

    def create(self, validated_data):
        """Cria uma campanha e associa as integrações"""
        integrations = validated_data.pop('integrations', [])
        validated_data['in_use'] = True
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
