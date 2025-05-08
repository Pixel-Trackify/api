from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
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

kwai_create_view_post_schema = extend_schema(
    summary="Criar uma nova conta Kwai",
    description="Cria uma nova conta Kwai com base nos dados fornecidos, incluindo campanhas associadas.",
    request=KwaiSerializer,
    responses={
        201: KwaiSerializer,

    },
    examples=[
        OpenApiExample(
            "Exemplo de Requisição",
            value={
                "name": "Conta da Marcela12",
                "campaigns": [
                    {
                        "uid": "72ddc00d-54e7-4e35-9dcd-e7eae9d61b91"
                    }
                ]
            },
            request_only=True,  # Indica que este exemplo é apenas para a requisição
        ),
        OpenApiExample(
            "Exemplo de Resposta",
            value={
                "uid": "9f96b8bc-40f3-415e-81a0-da1bfb7fcd5c",
                "name": "Conta da Marcela123",
                "user": "b77d099a-8577-4e93-b213-7e95884b16bd",
                "campaigns": [
                    {
                        "uid": "28f32ca0-8c69-4bf1-b74b-a3034f5c9ad4",
                        "title": "Gateway teste 3",
                        "in_use": True
                    }
                ],
                "created_at": None,
                "updated_at": None,
                "title": "zeroone pay",
                "total_approved": 0,
                "total_pending": 0,
                "amount_approved": 0,
                "amount_pending": 0,
                "total_abandoned": 0,
                "amount_abandoned": 0,
                "total_canceled": 0,
                "amount_canceled": 0,
                "total_refunded": 0,
                "amount_refunded": 0,
                "total_rejected": 0,
                "amount_rejected": 0,
                "total_chargeback": 0,
                "amount_chargeback": 0,
                "total_ads": 0,
                "profit": 0,
                "ROI": 0,
                "total_views": 0,
                "total_clicks": 0,
                "stats": {
                    "PIX": 0,
                    "CARD_CREDIT": 0,
                    "DEBIT_CARD": 0,
                    "BOLETO": 0
                },
                "overviews": []
            },
            response_only=True,  # Indica que este exemplo é apenas para a resposta
        ),
    ],
)
# Schema para KwaiDetailView
kwai_get_view_schema = extend_schema(
    summary="Obter detalhes de uma conta Kwai",
    description="Retorna os detalhes de uma conta Kwai específica, incluindo campanhas associadas e dados financeiros.",
    responses={
        200: KwaiSerializer,

    },
    examples=[
        OpenApiExample(
            "Exemplo de Resposta",
            value={
                "uid": "ef3dfc59-3232-4430-90d3-f8ddbdf87410",
                "name": "Conta da Marcela novo 2",
                "user": "251e36e4-738e-45ea-a315-7d9d86eff03c",
                "campaigns": [
                    {
                        "uid": "125456d5-bf0c-4510-96b0-4d14ec372356",
                        "title": "zeroone pay",
                        "in_use": True
                    }
                ],
                "created_at": "2025-04-23",
                "updated_at": "2025-04-23",
                "title": "zeroone pay",
                "total_approved": 0,
                "total_pending": 0,
                "amount_approved": 0.0,
                "amount_pending": 0,
                "total_abandoned": 0,
                "amount_abandoned": 0,
                "total_canceled": 0,
                "amount_canceled": 0,
                "total_refunded": 0,
                "amount_refunded": 0,
                "total_rejected": 0,
                "amount_rejected": 0,
                "total_chargeback": 0,
                "amount_chargeback": 0,
                "total_ads": 0.0,
                "profit": 0.0,
                "ROI": 0.0,
                "total_views": 0,
                "total_clicks": 0,
                "stats": {
                    "PIX": 0,
                    "CARD_CREDIT": 0,
                    "DEBIT_CARD": 0,
                    "BOLETO": 0
                },
                "overviews": [
                    {
                        "type": "EXPENSE",
                        "value": 0.0,
                        "date": "2025-04-23"
                    },
                    {
                        "type": "REVENUE",
                        "value": 0.0,
                        "date": "2025-04-23"
                    }
                ]
            },
            response_only=True,  # Indica que este exemplo é apenas para a resposta
        ),
    ],
)

kwai_put_view_schema = extend_schema(
    summary="Atualizar uma conta Kwai",
    description="Atualiza os dados de uma conta Kwai específica.(name - campaigns)",
    request=KwaiSerializer,
    responses={
        201: KwaiSerializer,

    },
    examples=[
        OpenApiExample(
            "Exemplo de Requisição",
            value={
                "name": "Conta da Marcela",
                "campaigns": [
                    {
                        "uid": "72ddc00d-54e7-4e35-9dcd-e7eae9d61b91"
                    }
                ]
            },
            request_only=True,  # Indica que este exemplo é apenas para a requisição
        ),
        OpenApiExample(
            "Exemplo de Resposta",
            value={
                "uid": "9f96b8bc-40f3-415e-81a0-da1bfb7fcd5c",
                "name": "Conta da Marcela123",
                "user": "b77d099a-8577-4e93-b213-7e95884b16bd",
                "campaigns": [
                    {
                        "uid": "28f32ca0-8c69-4bf1-b74b-a3034f5c9ad4",
                        "title": "Gateway teste 3",
                        "in_use": True
                    }
                ],
                "created_at": None,
                "updated_at": None,
                "title": "zeroone pay",
                "total_approved": 0,
                "total_pending": 0,
                "amount_approved": 0,
                "amount_pending": 0,
                "total_abandoned": 0,
                "amount_abandoned": 0,
                "total_canceled": 0,
                "amount_canceled": 0,
                "total_refunded": 0,
                "amount_refunded": 0,
                "total_rejected": 0,
                "amount_rejected": 0,
                "total_chargeback": 0,
                "amount_chargeback": 0,
                "total_ads": 0,
                "profit": 0,
                "ROI": 0,
                "total_views": 0,
                "total_clicks": 0,
                "stats": {
                    "PIX": 0,
                    "CARD_CREDIT": 0,
                    "DEBIT_CARD": 0,
                    "BOLETO": 0
                },
                "overviews": []
            },
            response_only=True,  # Indica que este exemplo é apenas para a resposta
        ),
    ],
)

kwai_delete_view_schema = extend_schema(
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

kwai_multiple_delete_schema = extend_schema(
    summary="Excluir múltiplas contas Kwai",
    description="Permite excluir múltiplas contas Kwai fornecendo uma lista de UIDs.",
    request=OpenApiTypes.OBJECT,
    responses={
        200: OpenApiExample(
            "Contas Excluídas",
            value={"detail": "Contas Kwai excluídas com sucesso."},
        ),
        400: OpenApiExample(
            "Erro de Validação",
            value={"error": "Alguns UIDs são inválidos ou não encontrados."},
        ),
    },
    examples=[
        OpenApiExample(
            "Exemplo de Requisição",
            value={
                "uids": [
                    "e5c17d14-1a2d-48da-8add-221d8e407cae",
                    "a12be829-5af2-43d6-b496-ca3116a3110e"
                ]
            },
            request_only=True,  # Indica que este exemplo é apenas para a requisição
        ),
        OpenApiExample(
            "Exemplo de Resposta",
            value={
                "detail": "Contas Kwai excluídas com sucesso."
            },
            response_only=True,  # Indica que este exemplo é apenas para a resposta
        ),
        OpenApiExample(
            "Exemplo de Resposta com Erro",
            value={
                "error": "Alguns UIDs são inválidos ou não encontrados.",
                "invalid_uids": [
                    "a12be829-5af2-43d6-b496-ca3116a3110e"
                ]
            },
            response_only=True,  # Indica que este exemplo é apenas para a resposta
        ),
    ],
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
dashboard_campaigns_get_schema = extend_schema(
    summary="Obter dados financeiros do dashboard de campanhas",
    description="Retorna os dados financeiros agregados e estatísticas do dashboard de campanhas. "
    "Permite filtrar os dados por intervalo de datas usando os parâmetros `start` e `end`. (?start=2025-04-20&end=2025-04-25)",
    parameters=[
        OpenApiParameter(
            name="start",
            description="Data inicial no formato YYYY-MM-DD. Filtra campanhas criadas a partir desta data.",
            required=False,
            type=OpenApiTypes.DATE,
        ),
        OpenApiParameter(
            name="end",
            description="Data final no formato YYYY-MM-DD. Filtra campanhas criadas até esta data.",
            required=False,
            type=OpenApiTypes.DATE,
        ),
    ],
    responses={
        200: OpenApiTypes.OBJECT,

    },
    examples=[
        OpenApiExample(
            "Exemplo de Resposta",
            value={
                "source": "Kwai",
                "title": "zeroone pay",
                "CPM": "2.22",
                "CPC": None,
                "CPV": None,
                "method": "CPM",
                "total_approved": 15,
                "total_pending": 0,
                "amount_approved": 150.0,
                "amount_pending": 0,
                "total_abandoned": 0,
                "amount_abandoned": 0,
                "total_canceled": 0,
                "amount_canceled": 0,
                "total_refunded": 0,
                "amount_refunded": 0,
                "total_rejected": 0,
                "amount_rejected": 0,
                "total_chargeback": 0,
                "amount_chargeback": 0,
                "total_ads": 0.40182,
                "profit": 149.59818,
                "ROI": 37230.14783,
                "total_views": 0,
                "total_clicks": 181,
                "created_at": "2025-04-23",
                "updated_at": "2025-04-23",
                "stats": {
                    "PIX": 3,
                    "CARD_CREDIT": 0,
                    "DEBIT_CARD": 0,
                    "BOLETO": 1
                },
                "overviews": [
                    {
                        "type": "EXPENSE",
                        "value": 0.40182,
                        "date": "2025-04-23"
                    },
                    {
                        "type": "REVENUE",
                        "value": 150.0,
                        "date": "2025-04-23"
                    }
                ]
            },
            response_only=True,  # Indica que este exemplo é apenas para a resposta
        ),
        OpenApiExample(
            "Erro Interno",
            value={
                "error": "Erro ao obter os dados financeiros do dashboard."
            },
            response_only=True,  # Indica que este exemplo é apenas para a resposta
        ),
    ],
)
