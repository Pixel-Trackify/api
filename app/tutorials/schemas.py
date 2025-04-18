from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes, OpenApiExample
from .serializers import TutorialSerializer

# Schema para a criação de tutoriais
tutorial_create_schema = extend_schema_view(
    post=extend_schema(
        summary="Criar um novo tutorial",
        description="Endpoint para criar um novo tutorial. Apenas administradores podem acessar.",
        tags=["Tutoriais"],
        request=TutorialSerializer,
        responses={201: TutorialSerializer},
        examples=[
            OpenApiExample(
                "Exemplo de Requisição",
                value={
                    "title": "Novo Tutorial",
                    "description": "Descrição do novo tutorial",
                    "youtube_url": "https://www.youtube.com/watch?v=example"
                },
                request_only=True,
            ),
            OpenApiExample(
                "Exemplo de Resposta",
                value={
                    "uid": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "Novo Tutorial",
                    "description": "Descrição do novo tutorial",
                    "youtube_url": "https://www.youtube.com/watch?v=example",
                    "thumbnail_url": "https://img.youtube.com/vi/example/default.jpg",
                    "created_at": "2025-04-03T12:00:00Z",
                    "updated_at": "2025-04-03T12:00:00Z"
                },
                response_only=True,
            )
        ],
    )
)

# Schema para a listagem de tutoriais
tutorial_list_schema = extend_schema_view(
    get=extend_schema(
        summary="Listar tutoriais",
        description=(
            "Endpoint para listar tutoriais com suporte a paginação, ordenação e busca. "
            "Os parâmetros opcionais permitem filtrar, ordenar e paginar os resultados."
        ),
        tags=["Tutoriais"],
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
                name="ordering",
                description=(
                    "Campo para ordenação. Use os campos disponíveis: `id`, `title`, `description`, `created_at`. "
                    "Exemplo: `?ordering=title` para ordenar por título."
                ),
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="order",
                description=(
                    "Direção da ordenação. Use `asc` para ascendente ou `desc` para descendente. "
                    "Exemplo: `?ordering=title&order=desc` para ordenar por título em ordem decrescente."
                ),
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                enum=["asc", "desc"],
            ),
            OpenApiParameter(
                name="search",
                description=(
                    "Palavra-chave para busca nos campos definidos: `id`, `title`, `description`, `created_at`. "
                    "Exemplo: `?search=Python` para buscar tutoriais relacionados a 'Python'."
                ),
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={200: TutorialSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Exemplo de Busca",
                value={
                    "page": 1,
                    "page_size": 10,
                    "ordering": "title",
                    "order": "desc",
                    "search": "Python"
                },
            )
        ],
    )
)

# Schema para recuperar, atualizar e deletar tutoriais
tutorial_detail_schema = extend_schema_view(
    get=extend_schema(
        summary="Recuperar um tutorial",
        description="Endpoint para recuperar os detalhes de um tutorial específico.",
        tags=["Tutoriais"],
        parameters=[
            OpenApiParameter(
                name="uid",
                description="UUID do tutorial a ser recuperado.",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            )
        ],
        responses={200: TutorialSerializer},
        examples=[
            OpenApiExample(
                "Exemplo de Resposta",
                value={
                    "uid": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "Título do Tutorial",
                    "description": "Descrição do Tutorial",
                    "youtube_url": "https://www.youtube.com/watch?v=abc123",
                    "thumbnail_url": "https://example.com/thumbnail.jpg"
                },
                response_only=True,
            )
        ],
    ),
    put=extend_schema(
        summary="Atualizar um tutorial",
        description="Endpoint para atualizar os detalhes de um tutorial específico.",
        tags=["Tutoriais"],
        parameters=[
            OpenApiParameter(
                name="uid",
                description="UUID do tutorial a ser atualizado.",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            )
        ],
        request=TutorialSerializer,
        responses={200: TutorialSerializer},
        examples=[
            OpenApiExample(
                "Exemplo de Requisição",
                value={
                    "title": "Novo Título",
                    "description": "Nova descrição",
                    "youtube_url": "https://www.youtube.com/watch?v=xyz456",
                    "thumbnail_url": "https://example.com/new-thumbnail.jpg"
                },
                request_only=True,
            ),
            OpenApiExample(
                "Exemplo de Resposta",
                value={
                    "uid": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "Novo Título",
                    "description": "Nova descrição",
                    "youtube_url": "https://www.youtube.com/watch?v=xyz456",
                    "thumbnail_url": "https://example.com/new-thumbnail.jpg"
                },
                response_only=True,
            )
        ],
    ),
    delete=extend_schema(
        summary="Deletar um tutorial",
        description="Endpoint para deletar um tutorial específico.",
        tags=["Tutoriais"],
        parameters=[
            OpenApiParameter(
                name="uid",
                description="UUID do tutorial a ser deletado.",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            )
        ],
        responses={204: None},
        examples=[
            OpenApiExample(
                "Exemplo de Requisição",
                value=None,
                request_only=True,
            )
        ],
    )
)
# Schema para deletar múltiplos tutoriais
tutorial_delete_multiple_schema = extend_schema_view(
    post=extend_schema(
        summary="Deletar múltiplos tutoriais",
        description="Endpoint para deletar vários tutoriais enviando os UUIDs no corpo da requisição. Apenas administradores podem acessar.",
        tags=["Tutoriais"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "uids": {
                        "type": "array",
                        "items": {"type": "string", "format": "uuid"},
                        "description": "Lista de UUIDs dos tutoriais a serem deletados."
                    }
                },
                "example": {
                    "uids": [
                        "123e4567-e89b-12d3-a456-426614174000",
                        "123e4567-e89b-12d3-a456-426614174001"
                    ]
                }
            }
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "2 tutorial(s) excluído(s) com sucesso."},
                    "not_found": {
                        "type": "array",
                        "items": {"type": "string", "format": "uuid"},
                        "example": ["123e4567-e89b-12d3-a456-426614174002"]
                    }
                }
            },
            400: {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Nenhum UUID fornecido."}
                }
            },
            404: {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Nenhum tutorial encontrado."}
                }
            }
        },
        examples=[
            OpenApiExample(
                "Exemplo de Requisição",
                value={
                    "uids": [
                        "123e4567-e89b-12d3-a456-426614174000",
                        "123e4567-e89b-12d3-a456-426614174001"
                    ]
                },
                request_only=True,
            ),
            OpenApiExample(
                "Exemplo de Resposta Sucesso",
                value={
                    "message": "2 tutorial(s) excluído(s) com sucesso.",
                    "not_found": []
                },
                response_only=True,
            ),
            OpenApiExample(
                "Exemplo de Resposta Erro",
                value={
                    "error": "Nenhum UUID fornecido."
                },
                response_only=True,
            )
        ],
    )
)
