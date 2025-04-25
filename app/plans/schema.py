from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from .serializers import PlanCreateSerializer, PlanUpdateSerializer, MultipleDeleteSerializer

plan_viewset_schema = extend_schema_view(
    list=extend_schema(
        summary="Listar Planos",
        description="Retorna uma lista de todos os planos disponíveis. Suporta filtros de ordenação e pesquisa.",
        parameters=[
            OpenApiParameter(
                name="ordering", description="Ordenar por campos como `created_at` ou `price`.", required=False, type=str),
            OpenApiParameter(
                name="search", description="Pesquisar planos pelo nome.", required=False, type=str),
        ],
        examples=[
            OpenApiExample(
                "Exemplo de Resposta",
                value=[
                    {
                        "uid": "e5c17d14-1a2d-48da-8add-221d8e407cae",
                        "name": "Plano Mensal",
                        "price": "29.99",
                        "duration": "month",
                        "duration_value": 1,
                        "is_current": False,
                        "description": "Plano mensal básico",
                        "created_at": "2025-04-25T12:00:00Z",
                        "features_response": [
                            {"text": "Acesso básico", "active": True}
                        ]
                    }
                ],
            )
        ],
    ),
    retrieve=extend_schema(
        summary="Detalhar Plano",
        description="Retorna os detalhes de um plano específico com base no UID.",
        examples=[
            OpenApiExample(
                "Exemplo de Resposta",
                value={
                    "uid": "e5c17d14-1a2d-48da-8add-221d8e407cae",
                    "name": "Plano Mensal",
                    "price": "29.99",
                    "duration": "month",
                    "duration_value": 1,
                    "is_current": False,
                    "description": "Plano mensal básico",
                    "created_at": "2025-04-25T12:00:00Z",
                    "features_response": [
                        {"text": "Acesso básico", "active": True}
                    ]
                },
            )
        ],
    ),
    create=extend_schema(
        summary="Criar Plano",
        description="Cria um novo plano. Apenas administradores podem realizar esta ação.",
        request=PlanCreateSerializer,  # Usando o serializer para o corpo da requisição
        responses={
            201: {
                "type": "object",
                "properties": {
                    "uid": {"type": "string", "example": "e5c17d14-1a2d-48da-8add-221d8e407cae"},
                    "name": {"type": "string", "example": "Plano Mensal"},
                    "price": {"type": "string", "example": "29.99"},
                    "duration": {"type": "string", "example": "month"},
                    "duration_value": {"type": "integer", "example": 1},
                    "is_current": {"type": "boolean", "example": False},
                    "description": {"type": "string", "example": "Plano mensal básico"},
                    "created_at": {"type": "string", "format": "date-time", "example": "2025-04-25T12:00:00Z"},
                    "features_response": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string", "example": "Acesso básico"},
                                "active": {"type": "boolean", "example": True},
                            },
                        },
                    },
                },
            }
        },
        examples=[
            OpenApiExample(
                "Exemplo de Requisição",
                value={
                    "name": "Plano Mensal",
                    "description": "Plano mensal básico",
                    "price": 29.99,
                    "duration": "month",
                    "duration_value": 1,
                    "features": [
                        {"text": "Acesso básico", "active": True},
                        {"text": "Suporte 24 horas", "active": True}
                    ]
                },
                request_only=True,
            ),
            OpenApiExample(
                "Exemplo de Resposta",
                value={
                    "uid": "e5c17d14-1a2d-48da-8add-221d8e407cae",
                    "name": "Plano Mensal",
                    "price": "29.99",
                    "duration": "month",
                    "duration_value": 1,
                    "is_current": False,
                    "description": "Plano mensal básico",
                    "created_at": "2025-04-25T12:00:00Z",
                    "features_response": [
                        {"text": "Acesso básico", "active": True},
                        {"text": "Suporte 24 horas", "active": True}
                    ]
                },
                response_only=True,
            ),
        ],
    ),
    update=extend_schema(
        summary="Atualizar Plano",
        description="Atualiza os dados de um plano existente. Apenas administradores podem realizar esta ação.",
        request=PlanUpdateSerializer,  # Usando o serializer para o corpo da requisição
        parameters=[
            OpenApiParameter(
                name="uid",
                description="UID do plano a ser atualizado.",
                required=True,
                type="uuid",
                location="path",
            )
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "uid": {"type": "string", "example": "e5c17d14-1a2d-48da-8add-221d8e407cae"},
                    "name": {"type": "string", "example": "Plano Atualizado"},
                    "price": {"type": "string", "example": "49.99"},
                    "duration": {"type": "string", "example": "month"},
                    "duration_value": {"type": "integer", "example": 1},
                    "is_current": {"type": "boolean", "example": True},
                    "description": {"type": "string", "example": "Plano atualizado com novas features"},
                    "created_at": {"type": "string", "format": "date-time", "example": "2025-04-25T12:00:00Z"},
                    "features_response": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string", "example": "Acesso ilimitado"},
                                "active": {"type": "boolean", "example": True},
                            },
                        },
                    },
                },
            }
        },
    ),
    destroy=extend_schema(
        summary="Excluir Plano",
        description="Exclui um plano com base no UID. Apenas administradores podem realizar esta ação.",
        examples=[
            OpenApiExample(
                "Exemplo de Resposta",
                value=None,
            )
        ],
    ),
)

multiple_delete_schema = extend_schema(
    summary="Excluir Múltiplos Planos",
    description="Permite que administradores excluam múltiplos planos de uma vez com base em uma lista de UIDs.",
    # Usando o serializer para o corpo da requisição
    request=MultipleDeleteSerializer,
    examples=[
        OpenApiExample(
            "Exemplo de Requisição",
            value={
                "uids": ["e5c17d14-1a2d-48da-8add-221d8e407cae", "a12be829-5af2-43d6-b496-ca3116a3110e"],
            },
            request_only=True,
        ),
        OpenApiExample(
            "Exemplo de Resposta",
            value={"detail": "2 planos foram excluídos com sucesso."},
            response_only=True,
        ),
    ],
)
