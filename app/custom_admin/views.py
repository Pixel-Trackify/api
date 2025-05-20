from datetime import timedelta, datetime
from collections import defaultdict
from rest_framework.viewsets import ViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.timezone import now
from django.db.models import Sum, Count, Q, Value
from django.db.models.functions import TruncDate
from .permissions import IsSuperUser
from accounts.models import Usuario
from payments.models import UserSubscription
from campaigns.models import FinanceLogs
from .serializers import DashboardSerializer, UsuarioSerializer, ConfigurationSerializer, CaptchaSerializer
from .models import Configuration
from rest_framework.views import APIView
from .schemas import admin_dashboard_schema, configuration_view_get_schema, configuration_view_post_schema, captcha_view_get_schema, captcha_view_post_schema
from django.db import models
import requests
from django.urls import reverse
import logging
logger = logging.getLogger('django')


class ConfigurationView(APIView):
    permission_classes = [IsSuperUser]

    @configuration_view_get_schema
    def get(self, request):
        config = Configuration.objects.first()
        if not config:
            empty_data = {
                "email_register_subject": "",
                "email_recovery_subject": "",
                "email_reminder_subject": "",
                "email_expired_subject": "",
                "email_subscription_paid_subject": "",
                "email_register": "",
                "email_recovery": "",
                "email_reminder": "",
                "email_expired": "",
                "email_subscription_paid": "",
                "require_email_confirmation": False,
                "default_pix": "",
                "firebanking_api_key": "",
                "zeroone_webhook": "",
                "zeroone_webhook_code": "",
                "zeroone_secret_key": "",
                "recaptchar_enable": False,
                "recaptchar_site_key": "",
                "recaptchar_secret_key": "",
                "days_to_reminder": 0,
                "days_to_expire": 0,
                "late_payment_interest": 0.0,
                "daily_late_payment_interest": 0.0,
            }
            return Response(empty_data, status=200)

        serializer = ConfigurationSerializer(config)
        return Response(serializer.data)

    @configuration_view_post_schema
    def post(self, request):
        config = Configuration.objects.first()
        data = request.data.copy()

        zeroone_webhook_url = config.zeroone_webhook if config and config.zeroone_webhook else data.get(
            'zeroone_webhook')
        zeroone_secret_key = config.zeroone_secret_key if config and config.zeroone_secret_key else data.get(
            'zeroone_secret_key')

        callback_url = request.build_absolute_uri(reverse('payment-webhook'))

        # Se não houver webhook/código, cadastra na ZeroOne
        if not (config and config.zeroone_webhook and config.zeroone_webhook_code):
            if not zeroone_secret_key:
                return Response({"detail": "Configuração da ZeroOne não cadastrada."}, status=400)

            webhook_payload = {
                "callbackUrl": callback_url,
                "name": data.get("name", "Webhook ZeroOne"),
                "onBuyApproved": True,
                "onRefound": True,
                "onChargeback": True,
                "onPixCreated": True
            }

            try:
                # Cria o webhook
                response = requests.post(
                    "https://pay.zeroonepay.com.br/api/v1/webhook.create",
                    json=webhook_payload,
                    headers={
                        "Authorization": zeroone_secret_key,
                    }
                )
            except Exception as e:
                return Response({"detail": f"Erro de conexão com ZeroOne: {str(e)}"}, status=500)

            if response.status_code == 200 and response.json().get("success"):
                # Busca todos os webhooks para pegar o id do recém-criado
                try:
                    get_response = requests.get(
                        "https://pay.zeroonepay.com.br/api/v1/webhook.getWebhooks",
                        headers={
                            "Authorization": zeroone_secret_key,
                        }
                    )
                    if get_response.status_code == 200:
                        webhooks = get_response.json().get('result', [])
                        for wh in webhooks:
                            if wh.get('callbackUrl') == callback_url:
                                data['zeroone_webhook'] = wh.get(
                                    'callbackUrl', '')
                                data['zeroone_webhook_code'] = wh.get('id', '')
                                break
                        else:
                            return Response({"detail": "Webhook recém-criado não encontrado na lista de webhooks."}, status=400)
                    else:
                        return Response({"detail": f"Erro ao buscar webhooks: {get_response.text}"}, status=400)
                except Exception as e:
                    return Response({"detail": f"Erro ao buscar webhooks na ZeroOne: {str(e)}"}, status=500)
            else:
                return Response({"detail": f"Falha ao cadastrar webhook na ZeroOne. Resposta: {response.text}"}, status=400)

        # Salva/atualiza a configuração normalmente
        if config:
            serializer = ConfigurationSerializer(
                config, data=data, partial=True)
        else:
            serializer = ConfigurationSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(serializer.data)


class CaptchaView(APIView):
    permission_classes = [IsSuperUser]

    @captcha_view_get_schema
    def get(self, request):
        config = Configuration.objects.first()
        if not config:
            return Response({"detail": "Not found."}, status=404)
        serializer = CaptchaSerializer(config)
        return Response(serializer.data)

    @captcha_view_post_schema
    def post(self, request):
        token = request.data.get("token")
        site_key = request.data.get("recaptchar_site_key")
        secret_key = request.data.get("recaptchar_secret_key")

        # Atualiza ou cria a configuração
        config = Configuration.objects.first()
        if not config:
            config = Configuration.objects.create(
                recaptchar_site_key=site_key,
                recaptchar_secret_key=secret_key
            )
        else:
            if site_key:
                config.recaptchar_site_key = site_key
            if secret_key:
                config.recaptchar_secret_key = secret_key
            config.save()

        # Validação básica
        if not token or not config.recaptchar_secret_key or not config.recaptchar_site_key:
            return Response({"detail": "Token ou configuração inválida."}, status=400)

        verify_url = config.recaptchar_site_key
        payload = {
            "secret": config.recaptchar_secret_key,
            "response": token
        }
        response = requests.post(verify_url, data=payload)
        result = response.json()
        if result.get("success"):
            return Response({"success": True})
        else:
            return Response({"success": False, "error-codes": result.get("error-codes")}, status=400)


class AdminDashboardViewSet(ViewSet):
    permission_classes = [IsSuperUser]

    def get_date_range(self, start, end):
        """Calcula o intervalo de datas com base nos parâmetros fornecidos."""
        if not start and not end:
            end_date = now().date()
            start_date = end_date - timedelta(days=30)
        elif start and not end:
            start_date = end_date = datetime.strptime(start, '%Y-%m-%d').date()
        else:
            start_date = datetime.strptime(start, '%Y-%m-%d').date()
            end_date = datetime.strptime(end, '%Y-%m-%d').date()
        return start_date, end_date

    def get_register_stats(self, start_date, end_date):
        """Obtém estatísticas de registros de usuários (REGISTER)."""
        stats = Usuario.objects.filter(
            date_joined__range=[start_date, end_date]
        ).annotate(
            type=Value("REGISTER", output_field=models.CharField()),
            date=TruncDate('date_joined')
        ).values(
            'type', 'date'
        ).annotate(
            value=Count('uid')
        ).order_by('date')
        return stats

    def get_subscription_stats(self, start_date, end_date):
        """Obtém estatísticas de assinaturas ativas (SUBSCRIPTION)."""
        stats = UserSubscription.objects.filter(
            start_date__range=[start_date, end_date],
            is_active=True
        ).annotate(

            type=Value("SUBSCRIPTION", output_field=models.CharField()),

            date=TruncDate('start_date')
        ).values(
            'type', 'date'
        ).annotate(
            value=Count('uid')  # Conta as assinaturas por data
        ).order_by('date')
        
        return stats

    def fill_missing_days(self, users, start_date, end_date):
        """Preenche os dias ausentes no intervalo de datas com valores 0."""
        user_data = defaultdict(lambda: defaultdict(int))
        for user in users:
            user_data[user['type']][user['date']] = user['value']

        return [
            {
                "type": user_type,
                "value": user_data[user_type].get(date, 0),
                "date": date
            }
            for date in (start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1))
            for user_type in ['REGISTER', 'SUBSCRIPTION']
        ]

    def get_finance_stats(self, finance_logs):
        """Calcula estatísticas financeiras agregadas."""
        return {
            "total_approved": finance_logs.aggregate(total=Sum('total_approved'))['total'] or 0,
            "total_pending": finance_logs.aggregate(total=Sum('total_pending'))['total'] or 0,
            "total_refunded": finance_logs.aggregate(total=Sum('total_refunded'))['total'] or 0,
            "total_abandoned": finance_logs.aggregate(total=Sum('total_abandoned'))['total'] or 0,
            "total_chargeback": finance_logs.aggregate(total=Sum('total_chargeback'))['total'] or 0,
            "total_rejected": finance_logs.aggregate(total=Sum('total_rejected'))['total'] or 0,
            "amount_approved": finance_logs.aggregate(total=Sum('amount_approved'))['total'] or 0,
            "amount_pending": finance_logs.aggregate(total=Sum('amount_pending'))['total'] or 0,
            "amount_refunded": finance_logs.aggregate(total=Sum('amount_refunded'))['total'] or 0,
            "amount_rejected": finance_logs.aggregate(total=Sum('amount_rejected'))['total'] or 0,
            "amount_chargeback": finance_logs.aggregate(total=Sum('amount_chargeback'))['total'] or 0,
            "amount_abandoned": finance_logs.aggregate(total=Sum('amount_abandoned'))['total'] or 0,
            "total_ads": finance_logs.aggregate(total=Sum('total_ads'))['total'] or 0,
            "profit": finance_logs.aggregate(total=Sum('profit'))['total'] or 0,
            "total_views": finance_logs.aggregate(total=Sum('total_views'))['total'] or 0,
            "total_clicks": finance_logs.aggregate(total=Sum('total_clicks'))['total'] or 0,
            "stats": {
                "PIX": finance_logs.aggregate(pix_amount=Sum('pix_amount')).get('pix_amount', 0) or 0,
                "CARD_CREDIT": finance_logs.aggregate(credit_card_amount=Sum('credit_card_amount')).get('credit_card_amount', 0) or 0,
                "DEBIT_CARD": finance_logs.aggregate(debit_card_amount=Sum('debit_card_amount')).get('debit_card_amount', 0) or 0,
                "BOLETO": finance_logs.aggregate(boleto_amount=Sum('boleto_amount')).get('boleto_amount', 0) or 0,
            },
        }

    @admin_dashboard_schema
    def list(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        user = request.query_params.get('user')

        # Obter intervalo de datas
        start_date, end_date = self.get_date_range(start, end)

        finance_logs = FinanceLogs.objects.filter(
            campaign__created_at__range=[start_date, end_date]
        )
        if user:
            finance_logs = finance_logs.filter(campaign__user__uid=user)

        # Obter estatísticas de usuários
        total_users = Usuario.objects.filter(
            date_joined__range=[start_date, end_date]).count()
        total_users_subscription = Usuario.objects.filter(
            subscription_active=True).count()

        # Obter estatísticas de REGISTER e SUBSCRIPTION
        register_stats = self.get_register_stats(start_date, end_date)
        subscription_stats = self.get_subscription_stats(start_date, end_date)
        users = list(register_stats) + list(subscription_stats)
        filled_users = self.fill_missing_days(users, start_date, end_date)

        finance_stats = self.get_finance_stats(finance_logs)

        top_users = Usuario.objects.order_by('-profit')[:10]

        response_data = {
            "total_users": total_users,
            "total_users_subscription": total_users_subscription,
            **finance_stats,
            "users": filled_users,
            "top_users": UsuarioSerializer(top_users, many=True).data,
        }

        serializer = DashboardSerializer(response_data)
        return Response(serializer.data)
