from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiExample
from .serializers import KwaiSerializer, CampaignSerializer, FinanceLogsSerializer

# Schema para KwaiListView
kwai_list_view_get_schema = extend_schema(
    summary="Listar todas as contas Kwai",
    description="Retorna uma lista de todas as contas Kwai cadastradas.",
    responses={
        200: KwaiSerializer(many=True),
    },
    examples=[
        OpenApiExample(
            "Exemplo de Resposta",
            value=[
                {
                    "uid": "5ea76aa3-b33d-48d8-872c-b1d45f4b475c",
                    "name": "Conta da Marcela",
                    "user": "251e36e4-738e-45ea-a315-7d9d86eff03c",
                    "campaigns": [],
                    "created_at": "2025-04-29T19:21:45.455057-03:00",
                    "updated_at": "2025-04-29T19:21:45.455068-03:00"
                }
            ],
        )
    ],
)

kwai_list_view_post_schema = extend_schema(
    summary="Criar uma nova conta Kwai",
    description="Cria uma nova conta Kwai com base nos dados fornecidos.",
    request=KwaiSerializer,
    responses={
        201: KwaiSerializer,
        400: OpenApiExample(
            "Erro de Validação",
            value={
                "error": "O campo 'campaigns' é obrigatório e não pode estar vazio."},
        ),
    },
)

# Schema para KwaiDetailView
kwai_detail_view_get_schema = extend_schema(
    summary="Obter detalhes de uma conta Kwai",
    description="Retorna os detalhes de uma conta Kwai específica, incluindo campanhas associadas e dados financeiros.",
    responses={
        200: KwaiSerializer,
        404: OpenApiExample(
            "Conta Não Encontrada",
            value={"error": "Conta Kwai não encontrada."},
        ),
    },
)

kwai_detail_view_put_schema = extend_schema(
    summary="Atualizar uma conta Kwai",
    description="Atualiza os dados de uma conta Kwai específica.",
    request=KwaiSerializer,
    responses={
        200: KwaiSerializer,
        404: OpenApiExample(
            "Conta Não Encontrada",
            value={"error": "Conta Kwai não encontrada."},
        ),
    },
)

kwai_detail_view_delete_schema = extend_schema(
    summary="Excluir uma conta Kwai",
    description="Exclui uma conta Kwai específica e libera as campanhas associadas.",
    responses={
        200: OpenApiExample(
            "Conta Excluída",
            value={"message": "Conta Kwai excluída com sucesso."},
        ),
        404: OpenApiExample(
            "Conta Não Encontrada",
            value={"error": "Conta Kwai não encontrada."},
        ),
    },
)

# Schema para CampaignsNotInUseView
campaigns_not_in_use_view_get_schema = extend_schema(
    summary="Listar campanhas não utilizadas",
    description="Retorna uma lista de todas as campanhas que não estão em uso.",
    responses={
        200: CampaignSerializer(many=True),
    },
    examples=[
        OpenApiExample(
            "Exemplo de Resposta",
            value=[
                {
                    "uid": "37428e2f-40cb-482f-adec-1a863bf2d661",
                    "title": "Campanha Exemplo",
                    "in_use": False
                }
            ],
        )
    ],
)

# Schema para KwaiOverview
kwai_overview_get_schema = extend_schema(
    summary="Obter dados financeiros agregados",
    description="Retorna os dados agregados de receitas e despesas dos últimos 30 dias.",
    responses={
        200: OpenApiExample(
            "Exemplo de Resposta",
            value={
                "stats": {
                    "boleto": 500,
                    "pix": 300,
                    "credit_card": 200,
                    "credit_debit": 0
                },
                "overviews": [
                    {
                        "type": "EXPENSE",
                        "value": 1000,
                        "date": "2025-04-10"
                    },
                    {
                        "type": "REVENUE",
                        "value": 1500,
                        "date": "2025-04-11"
                    }
                ]
            },
        ),
    },
)
kwai_overview_schema = extend_schema(
    summary="Obter dados agregados e registros de FinanceLogs",
    description="Retorna os dados agregados, estatísticas e registros de FinanceLogs dos últimos 30 dias.",
    responses={
        200: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            "Exemplo de Resposta",
            value={
                "summary": [
                    {
                        "profit": "149.59818",
                        "ROI": "37230.14783",
                        "total_views": 0,
                        "total_clicks": 181,
                        "total_ads": "0.40182000",
                        "total_approved": 15,
                        "total_pending": 0,
                        "total_refunded": 0,
                        "total_abandoned": 0,
                        "total_chargeback": 0,
                        "total_rejected": 0,
                        "amount_approved": "150.00",
                        "amount_pending": "0.00",
                        "amount_refunded": "0.00",
                        "amount_rejected": "0.00",
                        "amount_chargeback": "0.00",
                        "amount_abandoned": "0.00",
                        "credit_card_amount": "0.00",
                        "credit_card_total": 0,
                        "pix_amount": "30.00",
                        "pix_total": 3,
                        "debit_card_amount": "0.00",
                        "debit_card_total": 0,
                        "boleto_amount": "10.00",
                        "boleto_total": 1,
                        "date": "2025-04-23",
                        "campaign": 49
                    }
                ],
                "stats": {
                    "boleto": 1,
                    "pix": 3,
                    "credit_card": 0,
                    "credit_debit": 0
                },
                "overviews": [
                    {
                        "type": "EXPENSE",
                        "value": 0.40182,
                        "date": "2025-04-23"
                    },
                    {
                        "type": "REVENUE",
                        "value": 10.0,
                        "date": "2025-04-23"
                    },
                    {
                        "type": "REVENUE",
                        "value": 10.0,
                        "date": "2025-04-23"
                    },
                    {
                        "type": "REVENUE",
                        "value": 10.0,
                        "date": "2025-04-23"
                    },
                    {
                        "type": "REVENUE",
                        "value": 10.0,
                        "date": "2025-04-23"
                    },
                    {
                        "type": "REVENUE",
                        "value": 10.0,
                        "date": "2025-04-23"
                    }
                ]
            },
        )
    ]
)
