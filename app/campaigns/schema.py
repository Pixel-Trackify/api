from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, OpenApiTypes
from .serializers import CampaignSerializer, CampaignViewSerializer


schemas = {
    'campaign_view_set': extend_schema_view(
        list=extend_schema(
            summary="Listar campanhas",
            description="Endpoint para listar todas as campanhas associadas ao usuário autenticado.",
            tags=["Campanhas"],
            responses={200: CampaignSerializer(many=True)},
        ),
        create=extend_schema(
            summary="Criar uma nova campanha",
            description="Endpoint para criar uma nova campanha vinculada ao usuário autenticado.",
            tags=["Campanhas"],
            request=CampaignSerializer,
            responses={201: CampaignSerializer},
            examples=[
                OpenApiExample(
                    "Exemplo de Requisição",
                    value={
                        "title": "Campanha ZeroOne",
                        "integrations": ["90490bae-7ebe-4f44-9ebf-ce81ee03e60f"],
                        "CPM": 12,
                        "source": "Kwai"
                    },
                    request_only=True,
                ),
                OpenApiExample(
                    "Exemplo de Resposta",
                    value={
                        "uid": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Campanha ZeroOne",
                        "integrations": ["90490bae-7ebe-4f44-9ebf-ce81ee03e60f"],
                        "CPM": 12,
                        "source": "Kwai",
                        "created_at": "2025-03-20T12:00:00Z"
                    },
                    response_only=True,
                )
            ],
        ),
        retrieve=extend_schema(
            summary="Recuperar uma campanha",
            description="Endpoint para recuperar os detalhes de uma campanha específica usando o UUID como identificador.",
            tags=["Campanhas"],
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da campanha a ser recuperada.",
                    required=True,
                    type=OpenApiTypes.UUID,
                    location=OpenApiParameter.PATH,
                )
            ],
            responses={200: CampaignSerializer},
            examples=[
                OpenApiExample(
                    "Exemplo de Resposta",
                    value={
                        "uid": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Campanha ZeroOne",
                        "integrations": ["90490bae-7ebe-4f44-9ebf-ce81ee03e60f"],
                        "CPM": 12,
                        "source": "Kwai",
                        "created_at": "2025-03-20T12:00:00Z"
                    },
                    response_only=True,
                )
            ],
        ),
        update=extend_schema(
            summary="Atualizar uma campanha",
            description="Endpoint para atualizar completamente os detalhes de uma campanha específica.",
            tags=["Campanhas"],
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da campanha a ser atualizada.",
                    required=True,
                    type=OpenApiTypes.UUID,
                    location=OpenApiParameter.PATH,
                )
            ],
            request=CampaignSerializer,
            responses={200: CampaignSerializer},
            examples=[
                OpenApiExample(
                    "Exemplo de Requisição",
                    value={
                        "title": "Campanha Atualizada",
                        "integrations": ["90490bae-7ebe-4f44-9ebf-ce81ee03e60f"],
                        "CPM": 15,
                        "source": "Kwai"
                    },
                    request_only=True,
                ),
                OpenApiExample(
                    "Exemplo de Resposta",
                    value={
                        "uid": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Campanha Atualizada",
                        "integrations": ["90490bae-7ebe-4f44-9ebf-ce81ee03e60f"],
                        "CPM": 15,
                        "source": "Kwai",
                        "created_at": "2025-03-20T12:00:00Z"
                    },
                    response_only=True,
                )
            ],
        ),
        partial_update=extend_schema(
            summary="Atualizar parcialmente uma campanha",
            description="Endpoint para atualizar parcialmente os detalhes de uma campanha específica.",
            tags=["Campanhas"],
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da campanha a ser atualizada parcialmente.",
                    required=True,
                    type=OpenApiTypes.UUID,
                    location=OpenApiParameter.PATH,
                )
            ],
            request=CampaignSerializer,
            responses={200: CampaignSerializer},
            examples=[
                OpenApiExample(
                    "Exemplo de Requisição",
                    value={
                        "CPM": 20
                    },
                    request_only=True,
                ),
                OpenApiExample(
                    "Exemplo de Resposta",
                    value={
                        "uid": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Campanha ZeroOne",
                        "integrations": ["90490bae-7ebe-4f44-9ebf-ce81ee03e60f"],
                        "CPM": 20,
                        "source": "Kwai",
                        "created_at": "2025-03-20T12:00:00Z"
                    },
                    response_only=True,
                )
            ],
        ),

        destroy=extend_schema(
            summary="Deletar uma campanha",
            description="Endpoint para deletar uma campanha específica usando o UUID como identificador.",
            tags=["Campanhas"],
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da campanha a ser deletada.",
                    required=True,
                    type=OpenApiTypes.UUID,
                    location=OpenApiParameter.PATH,
                )
            ],
            responses={204: None},
        )
    ),
    'kwai_webhook_view': extend_schema_view(
        get=extend_schema(
            description="Atualiza a campanha com base na ação recebida (view ou click).",
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UID da campanha",
                    required=True,
                    type=str,
                    location=OpenApiParameter.PATH
                ),
                OpenApiParameter(
                    name="action",
                    description="Ação realizada (view ou click)",
                    required=False,
                    type=str,
                    location=OpenApiParameter.QUERY
                )
            ],
            responses={
                200: CampaignViewSerializer,
                400: OpenApiExample(
                    "Erro de validação",
                    value={"error": "Detalhes do erro"}
                )
            }
        )
    )
}
