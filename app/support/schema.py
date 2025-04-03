from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, OpenApiTypes
from .serializers import SupportSerializer, SupportReplySerializer

schemas = {

    'support_create_view': extend_schema_view(
        post=extend_schema(
            summary="Criar um novo ticket de suporte",
            description=(
                "Endpoint para criar um novo ticket de suporte. "
                "É possível anexar até 3 arquivos de no máximo 15 MB. "
                "Os arquivos serão enviados para o Bucket S3."
            ),
            tags=["Suporte"],
            request={
                "application/json": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "example": "Problema com pagamento"},
                        "description": {"type": "string", "example": "Erro ao tentar pagar com cartão de crédito."},
                    },
                    "required": ["title", "description"],
                },
                "multipart/form-data": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "example": "Problema com pagamento"},
                        "description": {"type": "string", "example": "Erro ao tentar pagar com cartão de crédito."},
                        "files": {
                            "type": "array",
                            "items": {"type": "string", "format": "binary"},
                            "example": ["file1.png", "file2.pdf"],
                        },
                    },
                    "required": ["title", "description"],
                },
            },
            responses={
                201: {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "example": "Ticket criado com sucesso."},
                        "uid": {"type": "string", "example": "123e4567-e89b-12d3-a456-426614174000"},
                    },
                },
                400: {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "Título e descrição são obrigatórios."},
                    },
                },
                500: {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "Erro ao fazer upload do arquivo: Detalhes do erro."},
                    },
                },
            },
            examples=[
                OpenApiExample(
                    "Exemplo de Requisição (JSON)",
                    value={
                        "title": "Problema com pagamento",
                        "description": "Erro ao tentar pagar com cartão de crédito.",
                    },
                    request_only=True,
                ),
                OpenApiExample(
                    "Exemplo de Requisição (Multipart)",
                    value={
                        "title": "Problema com pagamento",
                        "description": "Erro ao tentar pagar com cartão de crédito.",
                        "files": ["file1.png", "file2.pdf"],
                    },
                    request_only=True,
                ),
                OpenApiExample(
                    "Exemplo de Resposta (Sucesso)",
                    value={
                        "message": "Ticket criado com sucesso.",
                        "uid": "123e4567-e89b-12d3-a456-426614174000",
                    },
                    response_only=True,
                ),
                OpenApiExample(
                    "Exemplo de Resposta (Erro - Arquivo Grande)",
                    value={
                        "error": "O arquivo excede o tamanho máximo permitido de 15MB."
                    },
                    response_only=True,
                ),
            ],
        ),
    ),
    'support_reply_create_view': extend_schema_view(
        post=extend_schema(
            summary="Criar uma nova resposta para um ticket de suporte",
            description=(
                "Endpoint para criar uma nova resposta para um ticket de suporte. "
                "É possível anexar até 3 arquivos de no máximo 15 MB. "
                "Os arquivos serão enviados para o Bucket S3."
            ),
            tags=["Suporte"],
            request={
                "application/json": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string", "example": "Esta é uma resposta ao ticket."},
                    },
                    "required": ["description"],
                },
                "multipart/form-data": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string", "example": "Esta é uma resposta ao ticket."},
                        "files": {
                            "type": "array",
                            "items": {"type": "string", "format": "binary"},
                            "example": ["file1.png", "file2.pdf"],
                        },
                    },
                    "required": ["description"],
                },
            },
            responses={
                201: {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "example": "Resposta criada com sucesso."},
                        "uid": {"type": "string", "example": "123e4567-e89b-12d3-a456-426614174001"},
                    },
                },
                400: {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "Descrição é obrigatória."},
                    },
                },
                403: {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "Ticket de suporte não encontrado."},
                    },
                },
                404: {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "Ticket de suporte não encontrado."},
                    },
                },
                500: {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "Erro ao fazer upload do arquivo: Detalhes do erro."},
                    },
                },
            },
        ),
    ),
    'support_view_set': extend_schema_view(
        list=extend_schema(
            summary="Listar tickets de suporte",
            description="Endpoint para listar os tickets de suporte do usuário autenticado. Administradores podem ver todos os tickets.",
            tags=["Suporte"],
            responses={
                200: SupportSerializer(many=True),
            },
        ),
    ),
    'support_replies_view': extend_schema_view(
        retrieve=extend_schema(
            summary="Listar respostas de um ticket de suporte",
            description="Endpoint para listar as respostas de um ticket de suporte específico.",
            tags=["Suporte"],
            responses={
                200: SupportReplySerializer(many=True),
            },
        ),
    ),
}
