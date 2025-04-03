from drf_spectacular.utils import extend_schema
from rest_framework import status

# Esquema para GET /goals/
list_goals_schema = {
    "summary": "Listar Metas",
    "description": "Retorna uma lista de todas as metas disponíveis. Apenas administradores podem acessar.",
    "responses": {
        status.HTTP_200_OK: {
            "description": "Lista de metas retornada com sucesso.",
            "examples": {
                "application/json": [
                    {
                        "uid": "123e4567-e89b-12d3-a456-426614174000",
                        "prize": "Meta 1",
                        "description": "Descrição da meta 1",
                        "min": 100.0,
                        "max": 500.0,
                        "created_at": "2025-04-02T12:00:00Z",
                        "updated_at": "2025-04-02T12:00:00Z",
                    },
                    {
                        "uid": "123e4567-e89b-12d3-a456-426614174001",
                        "prize": "Meta 2",
                        "description": "Descrição da meta 2",
                        "min": 200.0,
                        "max": 600.0,
                        "created_at": "2025-04-02T12:10:00Z",
                        "updated_at": "2025-04-02T12:10:00Z",
                    },
                ]
            },
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Acesso negado.",
            "examples": {"detail": "Apenas administradores podem acessar as metas."},
        },
    },
}

# Esquema para POST /goals/
create_goal_schema = {
    "summary": "Criar Meta",
    "description": "Permite criar uma nova meta. Apenas administradores podem realizar essa ação.",
    "request": {
        "application/json": {
            "type": "object",
            "properties": {
                "prize": {"type": "string", "description": "Título da meta."},
                "description": {"type": "string", "description": "Descrição da meta."},
                "min": {"type": "number", "description": "Valor mínimo da meta."},
                "max": {"type": "number", "description": "Valor máximo da meta."},
            },
            "required": ["prize", "min", "max"],
        }
    },
    "responses": {
        status.HTTP_201_CREATED: {
            "description": "Meta criada com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "uid": "123e4567-e89b-12d3-a456-426614174000",
                        "prize": "Nova Meta",
                        "description": "Descrição da nova meta",
                        "min": 100.0,
                        "max": 500.0,
                        "created_at": "2025-04-02T12:00:00Z",
                        "updated_at": "2025-04-02T12:00:00Z",
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Erro de validação.",
            "content": {
                "application/json": {
                    "example": {"error": "Os valores 'min' e 'max' devem ser maiores que 0."}
                }
            },
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Acesso negado.",
            "content": {
                "application/json": {
                    "example": {"detail": "Apenas administradores podem criar metas."}
                }
            },
        },
    },
}

# Esquema para GET /goals/{uid}/
retrieve_goal_schema = {
    "summary": "Detalhar Meta",
    "description": "Retorna os detalhes de uma meta específica pelo `uid`. Apenas administradores podem acessar.",
    "responses": {
        status.HTTP_200_OK: {
            "description": "Detalhes da meta retornados com sucesso.",
            "examples": {
                "application/json": {
                    "uid": "123e4567-e89b-12d3-a456-426614174000",
                    "prize": "Meta 1",
                    "description": "Descrição da meta 1",
                    "min": 100.0,
                    "max": 500.0,
                    "created_at": "2025-04-02T12:00:00Z",
                    "updated_at": "2025-04-02T12:00:00Z",
                }
            },
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Meta não encontrada.",
            "examples": {"detail": "Meta não encontrada."},
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Acesso negado.",
            "examples": {"detail": "Apenas administradores podem acessar as metas."},
        },
    },
}

# Esquema para PUT /goals/{uid}/ e PATCH /goals/{uid}/
update_goal_schema = {
    "summary": "Atualizar Meta",
    "description": "Permite atualizar uma meta específica pelo `uid`. Apenas administradores podem realizar essa ação.",
    "request": {
        "application/json": {
            "type": "object",
            "properties": {
                "prize": {"type": "string", "description": "Título da meta."},
                "description": {"type": "string", "description": "Descrição da meta."},
                "min": {"type": "number", "description": "Valor mínimo da meta."},
                "max": {"type": "number", "description": "Valor máximo da meta."},
            },
        }
    },
    "responses": {
        status.HTTP_200_OK: {
            "description": "Meta atualizada com sucesso.",
            "examples": {
                "application/json": {
                    "uid": "123e4567-e89b-12d3-a456-426614174000",
                    "prize": "Meta Atualizada",
                    "description": "Descrição atualizada",
                    "min": 150.0,
                    "max": 600.0,
                    "created_at": "2025-04-02T12:00:00Z",
                    "updated_at": "2025-04-02T12:10:00Z",
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Erro de validação.",
            "examples": {"error": "O valor máximo não pode ser menor que o valor mínimo."},
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Acesso negado.",
            "examples": {"detail": "Apenas administradores podem atualizar metas."},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Meta não encontrada.",
            "examples": {"detail": "Meta não encontrada."},
        },
    },
}


# Esquema para DELETE /goals/{uid}/
delete_goal_schema = {
    "summary": "Deletar Meta",
    "description": "Permite deletar uma única meta pelo `uid`. Apenas administradores podem realizar essa ação.",
    "responses": {
        status.HTTP_200_OK: {
            "description": "Meta excluída com sucesso.",
            "examples": {"message": "Meta excluída com sucesso."},
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Acesso negado.",
            "examples": {"detail": "Apenas administradores podem deletar metas."},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Meta não encontrada.",
            "examples": {"detail": "Meta não encontrada."},
        },
    },
}

# Esquema para POST /goals/delete-multiple/
delete_multiple_goals_schema = {
    "summary": "Deletar Múltiplas Metas",
    "description": "Permite deletar várias metas enviando os UUIDs no corpo da requisição. Apenas administradores podem realizar essa ação.",
    "request": {
        "application/json": {
            "type": "object",
            "properties": {
                "uids": {
                    "type": "array",
                    "items": {"type": "string", "format": "uuid"},
                    "description": "Lista de UUIDs das metas a serem deletadas.",
                }
            },
            "required": ["uids"],
        }
    },
    "responses": {
        status.HTTP_200_OK: {
            "description": "Metas excluídas com sucesso.",
            "examples": {
                "message": "2 meta(s) excluída(s) com sucesso.",
                "not_found": ["123e4567-e89b-12d3-a456-426614174001"],
            },
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Acesso negado.",
            "examples": {"detail": "Apenas administradores podem deletar metas."},
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Nenhum UUID fornecido.",
            "examples": {"error": "Nenhum UUID fornecido."},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Nenhuma meta encontrada.",
            "examples": {"error": "Nenhuma meta encontrada."},
        },
    },
}
