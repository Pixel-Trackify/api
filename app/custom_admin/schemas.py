from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from .serializers import DashboardSerializer, ConfigurationSerializer


configuration_view_get_schema = extend_schema(
    summary="Obter configuração",
    description="Retorna a configuração global do sistema.",
    responses={200: ConfigurationSerializer}
)

configuration_view_post_schema = extend_schema(
    summary="Criar/Atualizar configuração",
    description=(
        "Cria ou atualiza a configuração global do sistema. "
        "Se os campos zeroone_webhook e zeroone_webhook_code estiverem vazios, "
        "o sistema irá cadastrar o webhook na ZeroOne automaticamente."
    ),
    request=ConfigurationSerializer,
    responses={
        200: ConfigurationSerializer,
        400: OpenApiResponse(description="Erro de validação ou integração com ZeroOne"),
        500: OpenApiResponse(description="Erro interno ao comunicar com ZeroOne"),
    },
    examples=[
        OpenApiExample(
            "Exemplo de configuração mínima",
            value={
                "email_register_subject": "Bem-vindo!",
                "email_recovery_subject": "Recupere sua senha",
                "email_reminder_subject": "Lembrete",
                "email_expired_subject": "Assinatura expirada",
                "email_subscription_paid_subject": "Pagamento recebido",
                "email_register": "Conteúdo do email de registro",
                "email_recovery": "Conteúdo do email de recuperação",
                "email_reminder": "Conteúdo do email de lembrete",
                "email_expired": "Conteúdo do email expirado",
                "email_subscription_paid": "Conteúdo do email pago",
                "require_email_confirmation": True,
                "default_pix": "zeroone",
                "firebanking_api_key": None,
                "zeroone_webhook": "https://pay.zeroonepay.com.br/api/v1/webhook.create",
                "zeroone_webhook_code": None,
                "zeroone_secret_key": "seu-secret-key",
                "recaptchar_enable": True,
                "recaptchar_site_key": "sua-chave-site",
                "recaptchar_secret_key": "sua-chave-secreta",
                "days_to_reminder": 3,
                "days_to_expire": 7,
                "late_payment_interest": 2.0,
                "daily_late_payment_interest": 0.0333
            },
            request_only=True,
        ),
        OpenApiExample(
            "Exemplo de configuração completa",
            value={
                "email_register_subject": "Bem-vindo!",
                "email_recovery_subject": "Recupere sua senha",
                "email_reminder_subject": "Lembrete",
                "email_expired_subject": "Assinatura expirada",
                "email_subscription_paid_subject": "Pagamento recebido",
                "email_register": "Conteúdo do email de registro",
                "email_recovery": "Conteúdo do email de recuperação",
                "email_reminder": "Conteúdo do email de lembrete",
                "email_expired": "Conteúdo do email expirado",
                "email_subscription_paid": "Conteúdo do email pago",
                "require_email_confirmation": True,
                "default_pix": "zeroone",
                "firebanking_api_key": None,
                "zeroone_webhook": "https://pay.zeroonepay.com.br/api/v1/webhook.create",
                "zeroone_webhook_code": None,
                "zeroone_secret_key": "seu-secret-key",
                "recaptchar_enable": True,
                "recaptchar_site_key": "sua-chave-site",
                "recaptchar_secret_key": "sua-chave-secreta",
                "days_to_reminder": 3,
                "days_to_expire": 7,
                "late_payment_interest": 2.0,
                "daily_late_payment_interest": 0.0333
            },
            request_only=True,
        ),
    ]
)
captcha_view_get_schema = extend_schema(
    summary="Obter configuração do captcha",
    description="Retorna as chaves de configuração do captcha.",
    responses={
        200: OpenApiResponse(
            description="Configuração do captcha retornada com sucesso.",
            response={
                "type": "object",
                "properties": {
                    "recaptchar_site_key": {"type": "string"},
                    "recaptchar_secret_key": {"type": "string"},
                }
            }
        ),
        404: OpenApiResponse(
            description="Configuração não encontrada."
        ),
    }
)

captcha_view_post_schema = extend_schema(
    summary="Validar captcha e salvar configuração",
    description="Salva/atualiza as chaves do captcha e valida o token recebido.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "token": {"type": "string"},
                "recaptchar_site_key": {"type": "string"},
                "recaptchar_secret_key": {"type": "string"},
            },
            "required": ["token", "recaptchar_site_key", "recaptchar_secret_key"]
        }
    },
    responses={
        200: OpenApiResponse(
            description="Captcha válido.",
            response={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"}
                }
            }
        ),
        400: OpenApiResponse(
            description="Token ou configuração inválida."
        ),
    },
    examples=[
        OpenApiExample(
            "Exemplo de requisição",
            value={
                "token": "token_do_captcha",
                "recaptchar_site_key": "https://www.recaptchar_site_key",
                "recaptchar_secret_key": "sua_secret_key"
            },
            request_only=True
        ),
        OpenApiExample(
            "Exemplo de resposta sucesso",
            value={"success": True},
            response_only=True
        ),
        OpenApiExample(
            "Exemplo de resposta erro",
            value={"success": False,
                   "error-codes": ["invalid-input-response"]},
            response_only=True
        ),
    ]
)

admin_dashboard_schema = extend_schema(
    summary="Obter estatísticas do dashboard administrativo",
    description="Retorna estatísticas como total de usuários, pagamentos, visualizações, cliques, e informações de usuários registrados e assinaturas.",
    parameters=[
        OpenApiParameter(
            name="start",
            description="Data de início do intervalo (formato YYYY-MM-DD).",
            required=False,
            type=OpenApiTypes.DATE
        ),
        OpenApiParameter(
            name="end",
            description="Data de término do intervalo (formato YYYY-MM-DD).",
            required=False,
            type=OpenApiTypes.DATE
        ),
        OpenApiParameter(
            name="user",
            description="ID do usuário para filtrar os dados.",
            required=False,
            type=OpenApiTypes.STR
        ),
    ],
    responses={
        200: DashboardSerializer,

    },
    examples=[
        OpenApiExample(
            "Exemplo de Resposta",
            value={
                "total_users": 13,
                "total_users_subscription": 5,
                "total_approved": 15,
                "total_pending": 0,
                "amount_approved": "150.00",
                "amount_pending": "0.00",
                "profit": "149.60",
                "total_views": 100,
                "total_clicks": 181,
                "stats": {
                    "PIX": 3,
                    "CARD_CREDIT": 0,
                    "DEBIT_CARD": 0,
                    "BOLETO": 1
                },
                "users": [
                    {
                        "type": "REGISTER",
                        "value": 5,
                        "date": "2025-04-01"
                    },
                    {
                        "type": "SUBSCRIPTION",
                        "value": 2,
                        "date": "2025-04-01"
                    }
                ],
                "top_users": [
                    {
                        "uid": "b77d099a-8577-4e93-b213-7e95884b16bd",
                        "name": "Marcos Lacerda",
                        "email": "marcos1@gmail.com",
                        "date_joined": "2025-04-03T22:46:41.387423-03:00",
                        "profit": "49.61",
                        "subscription_active": False
                    }
                ]
            },
        )
    ]
)

admin_subscription_report_schema = extend_schema(
    summary="Relatório de assinaturas (admin)",
    description="Retorna estatísticas de assinaturas e usuários em um intervalo de datas.",
    parameters=[
        OpenApiParameter(
            name="start",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Data inicial no formato YYYY-MM-DD (opcional, padrão: 30 dias atrás)"
        ),
        OpenApiParameter(
            name="end",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Data final no formato YYYY-MM-DD (opcional, padrão: hoje)"
        ),
    ],
    responses={
        200: OpenApiTypes.OBJECT,

    },
    examples=[
        OpenApiExample(
            'Exemplo de resposta',
            value={
                "total_users": 10,
                "total_subscriptions": 8,
                "amount_subscriptions": 1682.80,
                "overviews": [
                    {"date": "2025-04-20", "value": 265.50},
                    {"date": "2025-04-21", "value": 0.0}
                ]
            }
        )
    ]
)
