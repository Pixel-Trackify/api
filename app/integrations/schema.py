from drf_spectacular.utils import extend_schema, extend_schema_view
from .serializers import TransactionSerializer, IntegrationSerializer, IntegrationRequestSerializer

schemas = {
    'integration_view_set': extend_schema_view(
        list=extend_schema(
            description="Retorna as integrações do usuário autenticado.",
            responses={200: IntegrationSerializer(many=True)}
        ),
        create=extend_schema(
            description="Cria uma nova integração vinculada ao usuário autenticado.",
            request=IntegrationSerializer,
            responses={201: IntegrationSerializer}
        ),
        retrieve=extend_schema(
            description="Retorna os detalhes de uma integração específica do usuário autenticado.",
            parameters=[
                {
                    "name": "uid",
                    "required": True,
                    "in": "path",
                    "description": "UUID da integração",
                    "schema": {"type": "string", "format": "uuid"},
                }
            ],
            responses={200: IntegrationSerializer}
        ),
        update=extend_schema(
            description="Atualiza uma integração se o usuário autenticado for o proprietário.",
            request=IntegrationSerializer,
            responses={200: IntegrationSerializer}
        ),
        partial_update=extend_schema(
            description="Atualiza parcialmente uma integração se o usuário autenticado for o proprietário.",
            request=IntegrationSerializer,
            responses={200: IntegrationSerializer}
        ),
        destroy=extend_schema(
            description="Deleta uma integração se o usuário autenticado for o proprietário.",
            parameters=[
                {
                    "name": "uid",
                    "required": True,
                    "in": "path",
                    "description": "UUID da integração",
                    "schema": {"type": "string", "format": "uuid"},
                }
            ],
            responses={204: None}
        )
    ),
    'integration_detail_view': extend_schema_view(
        get=extend_schema(
            description="Retorna os detalhes de uma integração específica do usuário autenticado.",
            parameters=[
                {
                    "name": "uid",
                    "required": True,
                    "in": "path",
                    "description": "UUID da integração",
                    "schema": {"type": "string", "format": "uuid"},
                }
            ],
            responses={200: IntegrationSerializer}
        ),
        delete=extend_schema(
            description="Deleta uma integração específica do usuário autenticado.",
            parameters=[
                {
                    "name": "uid",
                    "required": True,
                    "in": "path",
                    "description": "UUID da integração",
                    "schema": {"type": "string", "format": "uuid"},
                }
            ],
            responses={204: None}
        )
    ),
    'integrationrequest_detail_view': extend_schema_view(
        get=extend_schema(
            description="Retorna os detalhes de uma requisição de integração específica.",
            parameters=[
                {
                    "name": "transaction_id",
                    "required": True,
                    "in": "path",
                    "description": "UUID da requisição de integração",
                    "schema": {"type": "string", "format": "uuid"},
                }
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
                {
                    "name": "uid",
                    "required": True,
                    "in": "path",
                    "description": "UUID da integração",
                    "schema": {"type": "string", "format": "uuid"},
                }
            ],
            responses={200: None}
        )
    ),
    'zeroone_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento ZeroOne.",
            parameters=[
                {
                    "name": "uid",
                    "required": True,
                    "in": "path",
                    "description": "UUID da integração",
                    "schema": {"type": "string", "format": "uuid"},
                }
            ],
            responses={200: None}
        )
    ),
    'ghostspay_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento GhostsPay.",
            parameters=[
                {
                    "name": "uid",
                    "required": True,
                    "in": "path",
                    "description": "UUID da integração",
                    "schema": {"type": "string", "format": "uuid"},
                }
            ],
            responses={200: None}
        )
    ),
    'paradisepag_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento ParadisePag.",
            parameters=[
                {
                    "name": "uid",
                    "required": True,
                    "in": "path",
                    "description": "UUID da integração",
                    "schema": {"type": "string", "format": "uuid"},
                }
            ],
            responses={200: None}
        )
    ),
    'disrupty_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento Disrupty.",
            parameters=[
                {
                    "name": "uid",
                    "required": True,
                    "in": "path",
                    "description": "UUID da integração",
                    "schema": {"type": "string", "format": "uuid"},
                }
            ],
            responses={200: None}
        )
    ),
    'wolfpay_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento WolfPay.",
            parameters=[
                {
                    "name": "uid",
                    "required": True,
                    "in": "path",
                    "description": "UUID da integração",
                    "schema": {"type": "string", "format": "uuid"},
                }
            ],
            responses={200: None}
        )
    ),
    'vegacheckout_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento Vega Checkout.",
            parameters=[
                {
                    "name": "uid",
                    "required": True,
                    "in": "path",
                    "description": "UUID da integração",
                    "schema": {"type": "string", "format": "uuid"},
                }
            ],
            responses={200: None}
        )
    ),
    'tribopay_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento Tribo Pay.",
            parameters=[
                {
                    "name": "uid",
                    "required": True,
                    "in": "path",
                    "description": "UUID da integração",
                    "schema": {"type": "string", "format": "uuid"},
                }
            ],
            responses={200: None}
        )
    ),
    'westpay_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento WestPay.",
            parameters=[
                {
                    "name": "uid",
                    "required": True,
                    "in": "path",
                    "description": "UUID da integração",
                    "schema": {"type": "string", "format": "uuid"},
                }
            ],
            responses={200: None}
        )
    )
}
