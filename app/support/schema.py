
from drf_spectacular.utils import extend_schema, OpenApiExample


# Documentação para SupportListView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from .serializers import SupportSerializer

support_list_view_schema = extend_schema(
    summary="Listar tickets de suporte",
    description="Retorna uma lista de tickets de suporte. Apenas administradores podem visualizar todos os tickets. Usuários comuns só podem visualizar seus próprios tickets.",
    parameters=[
        OpenApiParameter(
            name="ordering",
            description="Ordenar por campos, ex: `created_at` ou `-created_at`",
            required=False,
            type=str
        ),
        OpenApiParameter(
            name="search",
            description="Pesquisar por título ou descrição",
            required=False,
            type=str
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "count": {
                    "type": "integer",
                    "example": 1
                },
                "next": {
                    "type": ["string", "null"],
                    "example": None
                },
                "previous": {
                    "type": ["string", "null"],
                    "example": None
                },
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "uid": {
                                "type": "string",
                                "example": "7fcfa70c-f9e1-4ed0-863e-113e47a79fc1"
                            },
                            "title": {
                                "type": "string",
                                "example": "Problema com webhook"
                            },
                            "description": {
                                "type": "string",
                                "example": "Erro ao tentar pagar"
                            },
                            "created_at": {
                                "type": "string",
                                "format": "date-time",
                                "example": "2025-04-23T11:43:29.293239-03:00"
                            },
                            "updated_at": {
                                "type": "string",
                                "format": "date-time",
                                "example": "2025-04-23T11:56:03.131232-03:00"
                            },
                            "files": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "example": "https://onetracking.s3.sa-east-1.amazonaws.com/support_attachments/b77d099a-8577-4e93-b213-7e95884b16bd/20250423114329_d76d759541444fdd985b0a32aac4bbcd.png"
                                }
                            },
                            "role": {
                                "type": "string",
                                "example": "user"
                            },
                            "closed": {
                                "type": "boolean",
                                "example": False
                            },
                            "admin_read": {
                                "type": "boolean",
                                "example": False
                            },
                            "user_read": {
                                "type": "boolean",
                                "example": True
                            }
                        }
                    }
                }
            }
        },
        403: {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "Você não tem permissão para acessar este recurso."
                }
            }
        },
    },
    examples=[
        OpenApiExample(
            "Exemplo de resposta",
            value={
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "uid": "7fcfa70c-f9e1-4ed0-863e-113e47a79fc1",
                        "title": "Problema com webhook",
                        "description": "Erro ao tentar pagar",
                        "created_at": "2025-04-23T11:43:29.293239-03:00",
                        "updated_at": "2025-04-23T11:56:03.131232-03:00",
                        "files": [
                            "https://onetracking.s3.sa-east-1.amazonaws.com/support_attachments/b77d099a-8577-4e93-b213-7e95884b16bd/20250423114329_d76d759541444fdd985b0a32aac4bbcd.png",
                            "https://onetracking.s3.sa-east-1.amazonaws.com/support_attachments/b77d099a-8577-4e93-b213-7e95884b16bd/20250423114332_a6db3b25463e441083b5ce55a9c27a75.png",
                            "https://onetracking.s3.sa-east-1.amazonaws.com/support_attachments/b77d099a-8577-4e93-b213-7e95884b16bd/20250423114333_9ac791639f274cbb939298d314796a24.png"
                        ],
                        "role": "user",
                        "closed": False,
                        "admin_read": False,
                        "user_read": True
                    }
                ]
            },
            response_only=True,
        ),
    ],
)

# Documentação para SupportDetailView
support_detail_view_schema = extend_schema(
    summary="Detalhes de um ticket de suporte",
    description="Retorna os detalhes de um ticket de suporte específico, incluindo as respostas associadas.",
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "example": "Detalhes do ticket recuperados com sucesso."
                },
                "data": {
                    "type": "object",
                    "properties": {
                        "ticket": {
                            "type": "object",
                            "properties": {
                                "uid": {
                                    "type": "string",
                                    "example": "7fcfa70c-f9e1-4ed0-863e-113e47a79fc1"
                                },
                                "title": {
                                    "type": "string",
                                    "example": "Problema com webhook"
                                },
                                "description": {
                                    "type": "string",
                                    "example": "Erro ao tentar pagar"
                                },
                                "created_at": {
                                    "type": "string",
                                    "format": "date-time",
                                    "example": "2025-04-23T11:43:29.293239-03:00"
                                },
                                "updated_at": {
                                    "type": "string",
                                    "format": "date-time",
                                    "example": "2025-04-23T11:56:03.131232-03:00"
                                },
                                "files": {
                                    "type": "array",
                                    "items": {
                                        "type": "string",
                                        "example": "https://onetracking.s3.sa-east-1.amazonaws.com/support_attachments/b77d099a-8577-4e93-b213-7e95884b16bd/20250423114329_d76d759541444fdd985b0a32aac4bbcd.png"
                                    }
                                },
                                "role": {
                                    "type": "string",
                                    "example": "user"
                                },
                                "closed": {
                                    "type": "boolean",
                                    "example": False
                                },
                                "admin_read": {
                                    "type": "boolean",
                                    "example": False
                                },
                                "user_read": {
                                    "type": "boolean",
                                    "example": True
                                }
                            }
                        },
                        "replies": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {}
                            },
                            "example": []
                        }
                    }
                }
            }
        },
        404: {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "Ticket de suporte não encontrado."
                }
            }
        },
        403: {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "Você não tem permissão para acessar este ticket."
                }
            }
        },
    },
    examples=[
        OpenApiExample(
            "Exemplo de resposta",
            value={
                "message": "Detalhes do ticket recuperados com sucesso.",
                "data": {
                    "ticket": {
                        "uid": "7fcfa70c-f9e1-4ed0-863e-113e47a79fc1",
                        "title": "Problema com webhook",
                        "description": "Erro ao tentar pagar",
                        "created_at": "2025-04-23T11:43:29.293239-03:00",
                        "updated_at": "2025-04-23T11:56:03.131232-03:00",
                        "files": [
                            "https://onetracking.s3.sa-east-1.amazonaws.com/support_attachments/b77d099a-8577-4e93-b213-7e95884b16bd/20250423114329_d76d759541444fdd985b0a32aac4bbcd.png",
                            "https://onetracking.s3.sa-east-1.amazonaws.com/support_attachments/b77d099a-8577-4e93-b213-7e95884b16bd/20250423114332_a6db3b25463e441083b5ce55a9c27a75.png",
                            "https://onetracking.s3.sa-east-1.amazonaws.com/support_attachments/b77d099a-8577-4e93-b213-7e95884b16bd/20250423114333_9ac791639f274cbb939298d314796a24.png"
                        ],
                        "role": "user",
                        "closed": False,
                        "admin_read": False,
                        "user_read": True
                    },
                    "replies": []
                }
            },
            response_only=True,
        ),
    ],
)

# Documentação para SupportCreateView
support_create_view_schema = extend_schema(
    summary="Criar um ticket de suporte",
    description="Cria um novo ticket de suporte. Arquivos podem ser enviados opcionalmente.",
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "example": "Título do ticket"
                },
                "description": {
                    "type": "string",
                    "example": "Descrição do problema"
                },
                "files": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "format": "binary",
                        "example": "file1.png"
                    }
                }
            },
            "required": ["title", "description"]
        }
    },
    responses={
        201: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "example": "Ticket criado com sucesso."
                },
                "uid": {
                    "type": "string",
                    "example": "be17012e-e053-4fd0-91b2-e326381c9626"
                },
                "files": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "example": "https://bucket-name.s3.region.amazonaws.com/support_attachments/file1.png"
                    }
                }
            }
        },
        400: {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "Título e descrição são obrigatórios."
                }
            }
        },
        500: {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "Erro ao fazer upload do arquivo."
                }
            }
        },
    },
    examples=[
        OpenApiExample(
            "Exemplo de requisição com arquivos",
            value={
                "title": "Problema com pagamento",
                "description": "Erro ao tentar pagar com cartão de crédito.",
                "files": [
                    "file1.png",
                    "file2.png"
                ]
            },
            request_only=True,
        ),
        OpenApiExample(
            "Exemplo de resposta",
            value={
                "message": "Ticket criado com sucesso.",
                "uid": "be17012e-e053-4fd0-91b2-e326381c9626",
                "files": [
                    "https://bucket-name.s3.region.amazonaws.com/support_attachments/file1.png",
                    "https://bucket-name.s3.region.amazonaws.com/support_attachments/file2.png"
                ]
            },
            response_only=True,
        ),
    ],
)
# Documentação para SupportReplyCreateView

support_reply_create_view_schema = extend_schema(
    summary="Criar uma resposta para um ticket de suporte",
    description="Cria uma nova resposta para um ticket de suporte existente. O envio de arquivos é opcional.",
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "example": "Resolvido Problema com pagamento"
                },
                "description": {
                    "type": "string",
                    "example": "Resolvido Erro ao tentar pagar com cartão de crédito."
                },
                "files": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "format": "binary",
                        "example": "file1.png"
                    }
                }
            },
            "required": ["title", "description"]
        }
    },
    responses={
        201: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "example": "Resposta criada com sucesso."
                },
                "data": {
                    "type": "object",
                    "properties": {
                        "uid": {
                            "type": "string",
                            "example": "b861c2cd-e925-4880-be4b-180b673a2b21"
                        },
                        "support_uid": {
                            "type": "string",
                            "example": "7fcfa70c-f9e1-4ed0-863e-113e47a79fc1"
                        },
                        "description": {
                            "type": "string",
                            "example": "Resolvido Erro ao tentar pagar com cartão de crédito."
                        },
                        "created_at": {
                            "type": "string",
                            "format": "date-time",
                            "example": "2025-04-23T12:00:07.902529-03:00"
                        },
                        "role": {
                            "type": "string",
                            "example": "user"
                        }
                    }
                },
                "files": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "example": "https://bucket-name.s3.region.amazonaws.com/support_replies/file1.png"
                    }
                }
            }
        },
        404: {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "Ticket de suporte não encontrado."
                }
            }
        },
        403: {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "Você não tem permissão para responder a este ticket."
                }
            }
        },
    },
    examples=[
        OpenApiExample(
            "Exemplo de requisição sem arquivos",
            value={
                "title": "Resolvido Problema com pagamento",
                "description": "Resolvido Erro ao tentar pagar com cartão de crédito."
            },
            request_only=True,
        ),
        OpenApiExample(
            "Exemplo de requisição com arquivos",
            value={
                "title": "Resolvido Problema com pagamento",
                "description": "Resolvido Erro ao tentar pagar com cartão de crédito.",
                "files": [
                    "file1.png",
                    "file2.pdf"
                ]
            },
            request_only=True,
        ),
        OpenApiExample(
            "Exemplo de resposta",
            value={
                "message": "Resposta criada com sucesso.",
                "data": {
                    "uid": "b861c2cd-e925-4880-be4b-180b673a2b21",
                    "support_uid": "7fcfa70c-f9e1-4ed0-863e-113e47a79fc1",
                    "description": "Resolvido Erro ao tentar pagar com cartão de crédito.",
                    "created_at": "2025-04-23T12:00:07.902529-03:00",
                    "role": "user"
                },
                "files": []
            },
            response_only=True,
        ),
    ],
)
