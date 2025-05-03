from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .serializers import DashboardSerializer

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
