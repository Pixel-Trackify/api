from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, OpenApiTypes
from .serializers import TransactionSerializer, IntegrationSerializer, IntegrationRequestSerializer, DeleteMultipleSerializer

schemas = {
    'integration_view_set': extend_schema_view(
        list=extend_schema(
            summary="Listar integrações",
            description=(
                    "Endpoint para listar as integrações do usuário autenticado com suporte a paginação, ordenação e busca."
            ),
            tags=["Integrações"],
            parameters=[
                OpenApiParameter(
                    name="page",
                    description="Número da página para paginação.",
                    required=False,
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.QUERY,
                ),
                OpenApiParameter(
                    name="page_size",
                    description="Número de itens por página.",
                    required=False,
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.QUERY,
                ),

                OpenApiParameter(
                    name="search",
                    description=(
                        "Palavra-chave para busca nos campos definidos: `id`, `title`, `description`, `created_at`. "
                        "Exemplo: `?search=Python` para buscar integrações relacionadas a 'Python'."
                    ),
                    required=False,
                    type=OpenApiTypes.STR,
                    location=OpenApiParameter.QUERY,
                ),
            ],
            responses={200: IntegrationSerializer(many=True)},


        ),
        create=extend_schema(
            description="Cria uma nova integração vinculada ao usuário autenticado.",
            request=IntegrationSerializer,
            responses={201: IntegrationSerializer}
        ),
        retrieve=extend_schema(
            description="Retorna os detalhes de uma integração específica do usuário autenticado.",
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da integração",
                    required=True,
                    type=str,
                    location=OpenApiParameter.PATH
                )
            ],
            responses={200: IntegrationSerializer}
        ),
        update=extend_schema(
            description="Atualiza uma integração se o usuário autenticado for o proprietário.",
            request=IntegrationSerializer,
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da integração",
                    required=True,
                    type=str,
                    location=OpenApiParameter.PATH
                )
            ],
            responses={200: IntegrationSerializer}
        ),
        partial_update=extend_schema(
            description="Atualiza parcialmente uma integração se o usuário autenticado for o proprietário.",
            request=IntegrationSerializer,
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da integração",
                    required=True,
                    type=str,
                    location=OpenApiParameter.PATH
                )
            ],
            responses={200: IntegrationSerializer}
        ),
        destroy=extend_schema(
            description="Deleta uma integração se o usuário autenticado for o proprietário.",
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da integração",
                    required=True,
                    type=str,
                    location=OpenApiParameter.PATH
                )
            ],
            responses={204: None}
        ),
        delete_multiple=extend_schema(
            description="Permite deletar várias integrações enviando os UUIDs no corpo da requisição.",
            request=DeleteMultipleSerializer,  # Use o serializer aqui
            responses={
                200: OpenApiTypes.OBJECT,

            },
            examples=[
                OpenApiExample(
                    "Exemplo de Requisição",
                    value={
                        "uids": [
                            "54cc3376-3a92-4d39-8235-5d039e7df8d1",
                            "65406f8a-80b2-4a9e-b3d2-f2475a976f6b"
                        ]
                    },
                    request_only=True
                ),
                OpenApiExample(
                    "Exemplo de Resposta",
                    value={
                        "message": "2 integração(ões) excluída(s) com sucesso.",
                        "deleted_count": 2,
                        "deleted_uids": [
                            "54cc3376-3a92-4d39-8235-5d039e7df8d1",
                            "65406f8a-80b2-4a9e-b3d2-f2475a976f6b"
                        ],
                        "not_found": []
                    },
                    response_only=True
                )

            ]
        )
    ),
    'integration_detail_view': extend_schema_view(
        get=extend_schema(
            description="Retorna os detalhes de uma integração específica do usuário autenticado.",
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da integração",
                    required=True,
                    type=str,
                    location=OpenApiParameter.PATH
                )
            ],
            responses={200: IntegrationSerializer}
        ),
        delete=extend_schema(
            description="Deleta uma integração específica do usuário autenticado.",
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da integração",
                    required=True,
                    type=str,
                    location=OpenApiParameter.PATH
                )
            ],
            responses={204: None}
        )
    ),
    'integrationrequest_detail_view': extend_schema_view(
        get=extend_schema(
            description="Retorna os detalhes de uma requisição de integração específica.",
            parameters=[
                OpenApiParameter(
                    name="transaction_id",
                    description="UUID da requisição de integração",
                    required=True,
                    type=str,
                    location=OpenApiParameter.PATH
                )
            ],
            responses={200: IntegrationRequestSerializer}
        )
    ),
    'integrationrequest_list_view': extend_schema_view(
        get=extend_schema(
            description="Retorna uma lista de todas as requisições de integração do usuário autenticado.",
            responses={200: IntegrationRequestSerializer(many=True)}
        )
    ),
    'cloudfy_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento CloudFy.",
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da integração",
                    required=True,
                    type=str,
                    location=OpenApiParameter.PATH
                )
            ],
            responses={200: None}
        )
    ),
    'zeroone_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento ZeroOne.",
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da integração",
                    required=True,
                    type=str,
                    location=OpenApiParameter.PATH
                )
            ],
            responses={200: None}
        )
    ),
    'ghostspay_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento GhostsPay.",
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da integração",
                    required=True,
                    type=str,
                    location=OpenApiParameter.PATH
                )
            ],
            responses={200: None}
        )
    ),
    'paradisepag_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento ParadisePag.",
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da integração",
                    required=True,
                    type=str,
                    location=OpenApiParameter.PATH
                )
            ],
            responses={200: None}
        )
    ),
    'disrupty_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento Disrupty.",
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da integração",
                    required=True,
                    type=str,
                    location=OpenApiParameter.PATH
                )
            ],
            responses={200: None}
        )
    ),
    'wolfpay_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento WolfPay.",
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da integração",
                    required=True,
                    type=str,
                    location=OpenApiParameter.PATH
                )
            ],
            responses={200: None}
        )
    ),
    'vegacheckout_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento Vega Checkout.",
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da integração",
                    required=True,
                    type=str,
                    location=OpenApiParameter.PATH
                )
            ],
            responses={200: None}
        )
    ),
    'tribopay_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento Tribo Pay.",
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da integração",
                    required=True,
                    type=str,
                    location=OpenApiParameter.PATH
                )
            ],
            responses={200: None}
        )
    ),
    'westpay_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento WestPay.",
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da integração",
                    required=True,
                    type=str,
                    location=OpenApiParameter.PATH
                )
            ],
            responses={200: None}
        )
    ),

    'sunize_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento Sunize.",
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da integração associada ao webhook.",
                    required=True,
                    type=str,
                    location=OpenApiParameter.PATH
                )
            ],
            responses={200: None}
        )
    ),
}
