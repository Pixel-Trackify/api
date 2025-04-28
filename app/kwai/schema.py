from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes

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
