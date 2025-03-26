from drf_spectacular.utils import extend_schema, OpenApiExample

custom_token_verify_schema = extend_schema(
    summary="Verificar a validade de um token JWT",
    description=(
        "Este endpoint verifica se um token JWT é válido. "
        "Se o token for válido, retorna uma mensagem de sucesso e os dados do usuário, incluindo o avatar."
    ),

    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string", "example": "Token is valid"},
                "user": {
                    "type": "object",
                    "properties": {
                        "uid": {"type": "string", "example": "7c0fa97f-89d8-427f-a54a-ee9409ce0acb"},
                        "name": {"type": "string", "example": "João Gomes"},
                        "email": {"type": "string", "example": "joao.gomes@gmail.com"},
                        "avatar": {"type": "string", "example": "https://example.com/avatar.jpg"}
                    }
                }
            }
        },
        401: {
            "type": "object",
            "properties": {
                "message": {"type": "string", "example": "Token is invalid or expired"},
                "detail": {"type": "string", "example": "Token is invalid"}
            }
        },
        404: {
            "type": "object",
            "properties": {
                "message": {"type": "string", "example": "User not found"},
                "detail": {"type": "string", "example": "No user matching this token was found."}
            }
        }
    },
    examples=[
        OpenApiExample(
            "Exemplo de Requisição",
            value={"token": "seu_token_jwt_aqui"},
            request_only=True
        ),
        OpenApiExample(
            "Exemplo de Resposta (Sucesso)",
            value={
                "message": "Token is valid",
                "user": {
                    "uid": "7c0fa97f-89d8-427f-a54a-ee9409ce0acb",
                    "name": "João Gomes",
                    "email": "joao.gomes@gmail.com",
                    "avatar": "https://example.com/avatar.jpg"
                }
            },
            response_only=True
        ),
        OpenApiExample(
            "Exemplo de Resposta (Erro - Token Inválido)",
            value={
                "message": "Token is invalid or expired",
                "detail": "Token is invalid"
            },
            response_only=True
        ),
        OpenApiExample(
            "Exemplo de Resposta (Erro - Usuário Não Encontrado)",
            value={
                "message": "User not found",
                "detail": "No user matching this token was found."
            },
            response_only=True
        )
    ]
)
