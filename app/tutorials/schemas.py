from drf_spectacular.utils import extend_schema, extend_schema_view
from .serializers import TutorialSerializer

# Schema para a criação de tutoriais
tutorial_create_schema = extend_schema_view(
    post=extend_schema(
        summary="Criar um novo tutorial",
        description="Endpoint para criar um novo tutorial. Apenas administradores podem acessar.",
        tags=["Tutoriais"],
        responses={201: TutorialSerializer},
    )
)

# Schema para a listagem de tutoriais
tutorial_list_schema = extend_schema_view(
    get=extend_schema(
        summary="Listar tutoriais",
        description="Endpoint para listar tutoriais com suporte a paginação, ordenação e busca.",
        tags=["Tutoriais"],
        parameters=[
            {
                "name": "page",
                "required": False,
                "in": "query",
                "description": "Número da página para paginação.",
                "schema": {"type": "integer"},
            },
            {
                "name": "page_size",
                "required": False,
                "in": "query",
                "description": "Número de itens por página.",
                "schema": {"type": "integer"},
            },
            {
                "name": "ordering",
                "required": False,
                "in": "query",
                "description": "Campo para ordenação (ex: 'id', 'title').",
                "schema": {"type": "string"},
            },
            {
                "name": "search",
                "required": False,
                "in": "query",
                "description": "Palavra-chave para busca nos campos definidos.",
                "schema": {"type": "string"},
            },
        ],
        responses={200: TutorialSerializer(many=True)},
    )
)

# Schema para recuperar, atualizar e deletar tutoriais
tutorial_detail_schema = extend_schema_view(
    get=extend_schema(
        summary="Recuperar um tutorial",
        description="Endpoint para recuperar os detalhes de um tutorial específico.",
        tags=["Tutoriais"],
        responses={200: TutorialSerializer},
    ),
    put=extend_schema(
        summary="Atualizar um tutorial",
        description="Endpoint para atualizar os detalhes de um tutorial específico.",
        tags=["Tutoriais"],
        responses={200: TutorialSerializer},
    ),
    delete=extend_schema(
        summary="Deletar um tutorial",
        description="Endpoint para deletar um tutorial específico.",
        tags=["Tutoriais"],
        responses={204: None},
    )
)