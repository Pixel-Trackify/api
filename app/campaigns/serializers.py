from rest_framework import serializers
from .models import Campaign, CampaignView, Integration
from payments.models import UserSubscription
import logging
from django.db.models import Sum
from datetime import datetime, timedelta
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
            'total_ads', 'profit', 'ROI', 'total_views', 'total_clicks', 'in_use',
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

    def get_filtered_finance_logs(self, obj):
        """
        Retorna os FinanceLogs filtrados pelo intervalo de datas da request.
        """
        request = self.context.get('request')
        today = timezone.now().date()
        start_date = None
        end_date = None

        if request:
            start_date = request.query_params.get('start', None)
            end_date = request.query_params.get('end', None)

        try:
            if not start_date and not end_date:
                end_date = today
                start_date = end_date - timedelta(days=30)
            elif start_date and not end_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = start_date + timedelta(days=1)
            elif start_date and end_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            raise serializers.ValidationError(
                {"detail": "Os parâmetros de data devem estar no formato YYYY-MM-DD."})

        return obj.finance_logs.filter(date__gte=start_date, date__lte=end_date)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        finance_logs = self.get_filtered_finance_logs(instance)

        # Agregações filtradas
        data['total_approved'] = finance_logs.aggregate(
            total=Sum('total_approved'))['total'] or 0
        data['total_pending'] = finance_logs.aggregate(
            total=Sum('total_pending'))['total'] or 0
        data['amount_approved'] = str(finance_logs.aggregate(
            total=Sum('amount_approved'))['total'] or 0)
        data['amount_pending'] = str(finance_logs.aggregate(
            total=Sum('amount_pending'))['total'] or 0)
        data['total_abandoned'] = finance_logs.aggregate(
            total=Sum('total_abandoned'))['total'] or 0
        data['amount_abandoned'] = str(finance_logs.aggregate(
            total=Sum('amount_abandoned'))['total'] or 0)
        # data['total_canceled'] = finance_logs.aggregate(total=Sum('total_canceled'))['total'] or 0
        # data['amount_canceled'] = str(finance_logs.aggregate(total=Sum('amount_canceled'))['total'] or 0)
        data['total_refunded'] = finance_logs.aggregate(
            total=Sum('total_refunded'))['total'] or 0
        data['amount_refunded'] = str(finance_logs.aggregate(
            total=Sum('amount_refunded'))['total'] or 0)
        data['total_rejected'] = finance_logs.aggregate(
            total=Sum('total_rejected'))['total'] or 0
        data['amount_rejected'] = str(finance_logs.aggregate(
            total=Sum('amount_rejected'))['total'] or 0)
        data['total_chargeback'] = finance_logs.aggregate(
            total=Sum('total_chargeback'))['total'] or 0
        data['amount_chargeback'] = str(finance_logs.aggregate(
            total=Sum('amount_chargeback'))['total'] or 0)
        data['total_ads'] = str(finance_logs.aggregate(
            total=Sum('total_ads'))['total'] or 0)
        data['total_views'] = finance_logs.aggregate(
            total=Sum('total_views'))['total'] or 0
        data['total_clicks'] = finance_logs.aggregate(
            total=Sum('total_clicks'))['total'] or 0

        # Calcula profit e ROI filtrados
        amount_approved = finance_logs.aggregate(
            total=Sum('amount_approved'))['total'] or 0
        total_ads = finance_logs.aggregate(
            total=Sum('total_ads'))['total'] or 0
        profit = float(amount_approved) - float(total_ads)
        data['profit'] = f"{profit:.5f}"
        data['ROI'] = f"{(profit / float(total_ads) * 100) if total_ads else 0:.5f}"

        # Stats filtrados
        data['stats'] = {
            "CREDIT_CARD": finance_logs.aggregate(total=Sum('credit_card_amount'))['total'] or 0,
            "DEBIT_CARD": finance_logs.aggregate(total=Sum('debit_card_amount'))['total'] or 0,
            "PIX": finance_logs.aggregate(total=Sum('pix_amount'))['total'] or 0,
            "BOLETO": finance_logs.aggregate(total=Sum('boleto_amount'))['total'] or 0,
        }

        return data

    def get_overviews(self, obj):
        """
        Obtém os dados de despesas (EXPENSE) e receitas (REVENUE) diretamente da tabela FinanceLogs,
        filtrando pelo intervalo de datas informado via query params (?start=YYYY-MM-DD&end=YYYY-MM-DD).
        """
        request = self.context.get('request')
        today = timezone.now().date()
        start_date = None
        end_date = None

        if request:
            start_date = request.query_params.get('start', None)
            end_date = request.query_params.get('end', None)

        try:
            if not start_date and not end_date:
                end_date = today
                start_date = end_date - timedelta(days=30)
            elif start_date and not end_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = start_date + timedelta(days=1)
            elif start_date and end_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            raise serializers.ValidationError(
                {"detail": "Os parâmetros de data devem estar no formato YYYY-MM-DD."})

        # Obtém os registros de FinanceLogs associados à campanha no intervalo filtrado
        finance_logs = obj.finance_logs.filter(
            date__gte=start_date, date__lte=end_date)

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
        user = self.context['request'].user

        # Validação de assinatura ativa
        subscription = UserSubscription.objects.filter(
            user=user, is_active=True).first()
        if not subscription or not subscription.is_active:
            raise serializers.ValidationError(
                "Assinatura inativa. Não é possível cadastrar campanhas."
            )

        plan = subscription.plan
        campaign_count = Campaign.objects.filter(
            user=user, deleted=False).count()
        if campaign_count >= plan.campaign_limit:
            raise serializers.ValidationError(
                "Limite de campanhas atingido para seu plano."
            )

        # Validação já existente
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
