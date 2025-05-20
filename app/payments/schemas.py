from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .serializers import PaymentSerializer

# Schema para o endpoint PaymentStatusView
payment_status_schema = {
    "summary": "Verificar o status de um pagamento",
    "description": "Retorna o status de um pagamento com base no UID fornecido.",
    "parameters": [
        OpenApiParameter(
            name="uid",
            description="UID do pagamento",
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
        )
    ],
    "responses": {
        200: OpenApiResponse(
            description="Pagamento encontrado",
            examples=[
                OpenApiExample(
                    "Exemplo de Resposta",
                    value={"status": True},
                )
            ],
        ),
        404: OpenApiResponse(
            description="Pagamento não encontrado",
            examples=[
                OpenApiExample(
                    "Pagamento Não Encontrado",
                    value={"detail": "Not found."},
                )
            ],
        ),
    },
}

# Schema para o endpoint PaymentView
payment_create_schema = {
    "summary": "Criar um pagamento",
    "description": "Cria um pagamento para um plano e retorna os detalhes do pagamento.",
    "request": PaymentSerializer,  # Use o serializer para definir o corpo da requisição
    "responses": {
        201: OpenApiResponse(
            description="Pagamento criado com sucesso",
            examples=[
                OpenApiExample(
                    "Exemplo de Resposta",
                    value={
                        "message": "Pagamento criado com sucesso.",
                        "payment": {
                            "uid": "1459dbfe-453a-4c1e-a5ae-6f1945e80eec",
                            "status": False,
                            "price": 29.99,
                            "payment_method": "PIX",
                            "gateway_response": {
                                "id": "135bef63-28fa-4436-908c-cf11d0cc806a",
                                "customId": "ZER404781005300500",
                                "installments": None,
                                "expiresAt": "2025-05-08T03:00:00.000Z",
                                "dueAt": None,
                                "approvedAt": None,
                                "refundedAt": None,
                                "rejectedAt": None,
                                "chargebackAt": None,
                                "availableAt": None,
                                "pixQrCode": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAOQAAADkCAYAAACIV4iNAAAAAklEQVR4AewaftIAAAxISURB",
                                "billetUrl": None,
                                "billetCode": None,
                                "status": "PENDING",
                                "address": "",
                                "district": "",
                                "number": "",
                                "complement": "",
                                "city": "",
                                "state": "",
                                "zipCode": "",
                                "amount": 2999,
                                "taxSeller": 1.2,
                                "taxPlatform": 1,
                                "amountSeller": 2963,
                                "amountGarantee": 0,
                                "taxGarantee": 0,
                                "traceable": False,
                                "method": "PIX",
                                "deliveryStatus": None,
                                "createdAt": "2025-05-08T00:27:28.652Z",
                                "updatedAt": "2025-05-08T00:27:28.652Z",
                                "utmQuery": "",
                                "checkoutUrl": "",
                                "referrerUrl": "",
                                "externalId": "",
                                "postbackUrl": ""
                            }
                        }
                    },
                )
            ],
        ),
        400: OpenApiResponse(
            description="Erro de validação",
            examples=[
                OpenApiExample(
                    "Erro de Validação",
                    value={"plan_uid": ["Este campo é obrigatório."]},
                )
            ],
        ),
        404: OpenApiResponse(
            description="Plano não encontrado",
            examples=[
                OpenApiExample(
                    "Plano Não Encontrado",
                    value={"error": "Plano não encontrado."},
                )
            ],
        ),
    },
}

payment_change_plan_schema = {
    "summary": "Trocar de plano",
    "description": (
        "Troca o plano do usuário. Cria uma nova assinatura inativa e um pagamento para o novo plano. "
        "A assinatura só será ativada após o pagamento aprovado via webhook."
    ),
    "parameters": [
        OpenApiParameter(
            name="uid",
            description="UID da assinatura atual (UserSubscription)",
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
        )
    ],
    "request": PaymentSerializer,
    "responses": {
        201: OpenApiResponse(
            description="Solicitação de troca de plano criada com sucesso",
            examples=[
                OpenApiExample(
                    "Exemplo de Resposta",
                    value={
                        "message": "Solicitação de troca de plano criada com sucesso.",
                        "payment": {
                            "uid": "1459dbfe-453a-4c1e-a5ae-6f1945e80eec",
                            "status": False,
                            "price": 29.99,
                            "payment_method": "PIX",
                            "gateway_response": {
                                "id": "135bef63-28fa-4436-908c-cf11d0cc806a",
                                "customId": "ZER404781005300500",
                                "expiresAt": "2025-05-08T03:00:00.000Z",
                                "pixQrCode": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAOQAAADkCAYAAACIV4iNAAAAAklEQVR4AewaftIAAAxISURB",
                                "status": "PENDING",
                                "amount": 2999,
                                "method": "PIX",
                                "createdAt": "2025-05-08T00:27:28.652Z",
                                "updatedAt": "2025-05-08T00:27:28.652Z"
                            }
                        }
                    },
                )
            ],
        ),
        400: OpenApiResponse(
            description="Erro de validação",
            examples=[
                OpenApiExample(
                    "Erro de Validação",
                    value={"plan_uid": ["Este campo é obrigatório."]},
                )
            ],
        ),
        404: OpenApiResponse(
            description="Plano não encontrado",
            examples=[
                OpenApiExample(
                    "Plano Não Encontrado",
                    value={"error": "Plano não encontrado."},
                )
            ],
        ),
    },
}

# Schema para o endpoint PaymentWebhookView
payment_webhook_schema = {
    "summary": "Webhook para notificações de pagamento",
    "description": "Recebe notificações do gateway de pagamento e atualiza o estado do pagamento e da assinatura.",
    "request": {
        "type": "object",
        "properties": {
            "paymentId": {"type": "string", "example": "123e4567-e89b-12d3-a456-426614174000"},
            "status": {"type": "string", "example": "APPROVED"},
        },
        "required": ["paymentId", "status"],
    },
    "responses": {
        200: OpenApiResponse(
            description="Estado do pagamento atualizado com sucesso",
            examples=[
                OpenApiExample(
                    "Exemplo de Resposta",
                    value={"message": "Estado do pagamento atualizado com sucesso."},
                )
            ],
        ),
        400: OpenApiResponse(
            description="Erro de validação",
            examples=[
                OpenApiExample(
                    "Erro de Validação",
                    value={"error": "Dados inválidos."},
                )
            ],
        ),
        404: OpenApiResponse(
            description="Pagamento não encontrado",
            examples=[
                OpenApiExample(
                    "Pagamento Não Encontrado",
                    value={"error": "Pagamento não encontrado."},
                )
            ],
        ),
    },
}


subscription_info_schema = {
    "summary": "Informações da assinatura do usuário",
    "description": "Retorna informações detalhadas sobre a assinatura, pagamentos em aberto, histórico de pagamentos e planos disponíveis para o usuário autenticado.",
    "responses": {
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    'Exemplo de resposta',
                    value={
                        "plan": {
                            "uid": "60a65e44-11d6-4fa9-8f55-3daffe065873",
                            "name": "PRO",
                            "price": 499.29,
                            "status": "active",
                            "method": "PIX",
                            "duration": "days",
                            "duration_value": "14",
                            "expiration": "2025-04-25 14:32:10",
                        },
                        "payments_opened": [
                            {
                                "uid": "60a65e44-11d6-4fa9-8f55-3daffe065873",
                                "amount": 499.29,
                                "date": "2025-05-25 14:32:10"
                            }
                        ],
                        "payments_historic": [
                            {
                                "uid": "60a65e44-11d6-4fa9-8f55-3daffe065873",
                                "amount": 499.29,
                                "status": "paid",
                                "data": "2025-04-25 14:32:10"
                            }
                        ],
                        "plans": [
                            {
                                "uid": "60a65e44-11d6-4fa9-8f55-3daffe065873",
                                "amount": 499.29,
                                "name": "PRO",
                                "duration": "days",
                                "duration_value": "14",
                            }
                        ]
                    },
                    response_only=True
                )
            ]
        )
    },
    "tags": ["Assinatura e Pagamentos"]
}
