from drf_spectacular.utils import extend_schema, extend_schema_view
from .serializers import SubscriptionSerializer, SubscriptionPaymentSerializer

schemas = {
    'create_payment_view': extend_schema_view(
        post=extend_schema(
            description="Cria um novo pagamento para uma assinatura.",
            request=SubscriptionPaymentSerializer,
            responses={201: SubscriptionPaymentSerializer}
        )
    ),
    'payment_status_check_view': extend_schema_view(
        get=extend_schema(
            description="Verifica o status de um pagamento específico.",
            responses={200: SubscriptionPaymentSerializer}
        )
    ),
    'payment_status_view': extend_schema_view(
        get=extend_schema(
            description="Verifica o status de um pagamento PIX específico.",
            responses={200: SubscriptionPaymentSerializer}
        )
    ),
    'payment_webhook_view': extend_schema_view(
        post=extend_schema(
            description="Processa notificações de pagamento via webhook.",
            responses={200: None}
        )
    ),
    'transaction_status_view': extend_schema_view(
        get=extend_schema(
            description="Verifica o status de uma transação específica.",
            responses={200: SubscriptionPaymentSerializer}
        )
    )
}