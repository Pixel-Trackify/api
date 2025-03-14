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
            request=IntegrationRequestSerializer,
            responses={201: IntegrationSerializer}
        ),
        retrieve=extend_schema(
            description="Retorna os detalhes de uma integração específica do usuário autenticado.",
            responses={200: IntegrationSerializer}
        ),
        update=extend_schema(
            description="Atualiza uma integração se o usuário autenticado for o proprietário.",
            request=IntegrationRequestSerializer,
            responses={200: IntegrationSerializer}
        ),
        partial_update=extend_schema(
            description="Atualiza parcialmente uma integração se o usuário autenticado for o proprietário.",
            request=IntegrationRequestSerializer,
            responses={200: IntegrationSerializer}
        ),
        destroy=extend_schema(
            description="Deleta uma integração se o usuário autenticado for o proprietário.",
            responses={204: None}
        )
    ),
    'integration_detail_view': extend_schema_view(
        get=extend_schema(
            description="Retorna os detalhes de uma integração específica do usuário autenticado.",
            responses={200: IntegrationSerializer}
        ),
        delete=extend_schema(
            description="Deleta uma integração específica do usuário autenticado.",
            responses={204: None}
        )
    ),
    'transaction_detail_view': extend_schema_view(
        get=extend_schema(
            description="Retorna os detalhes de uma transação específica.",
            responses={200: TransactionSerializer}
        )
    ),
    'transaction_list_view': extend_schema_view(
        get=extend_schema(
            description="Retorna uma lista de todas as transações do usuário autenticado.",
            responses={200: TransactionSerializer(many=True)}
        )
    ),
    'cloudfy_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento CloudFy.",
            responses={200: None}
        )
    ),
    'zeroone_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento ZeroOne.",
            responses={200: None}
        )
    ),
    'ghostspay_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento GhostsPay.",
            responses={200: None}
        )
    ),
    'paradisepag_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento ParadisePag.",
            responses={200: None}
        )
    ),
    'disrupty_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento Disrupty.",
            responses={200: None}
        )
    ),
    'wolfpay_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento WolfPay.",
            responses={200: None}
        )
    ),
    'vegacheckout_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento Vega Checkout.",
            responses={200: None}
        )
    ),
    'tribopay_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de transações do gateway de pagamento Tribo Pay.",
            responses={200: None}
        )
    )
}
