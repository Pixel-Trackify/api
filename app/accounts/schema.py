from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiParameter, extend_schema
from .serializers import RegisterSerializer, UserProfileSerializer, ChangePasswordSerializer, LoginSerializer, MultipleDeleteSerializer
from drf_spectacular.types import OpenApiTypes


register_view_schema = extend_schema_view(
    post=extend_schema(
        summary="Registrar um novo usuário",
        description=(
            "Endpoint para registrar um novo usuário. O campo `avatar` é opcional e pode ser usado para fornecer a URL de uma imagem de avatar. "
            "O campo `plan_uid` também é opcional e pode ser usado para associar o usuário a um plano específico."
        ),
        tags=["Usuários"],
        request=RegisterSerializer,
        responses={
            201: OpenApiExample(
                "Sucesso",
                value={
                    "message": "Usuário registrado com sucesso!",
                    "user": {
                        "uid": "7c0fa97f-89d8-427f-a54a-ee9409ce0acb",
                        "name": "João Gomes",
                        "email": "joao.gomes1@gmail.com",
                        "avatar": None
                    },
                    "require_email_confirmation": True
                },
                response_only=True,
            ),
            400: OpenApiExample(
                "Erro - Dados inválidos",
                value={
                    "email": ["Este campo é obrigatório."],
                    "password": ["As senhas não coincidem."],
                    "cpf": ["CPF inválido."],
                    "plan_uid": ["Plano não encontrado."],
                    "avatar": ["URL inválida para o avatar."]
                },
                response_only=True,
            ),
        },
        examples=[
            OpenApiExample(
                "Exemplo de Requisição",
                value={
                    "email": "joao.gomes@gmail.com",
                    "cpf": "17464185080",
                    "name": "João Gomes",
                    "password": "Password123!",
                    "confirm_password": "Password123!",
                    "plan_uid": "191663b0-d352-4f5e-a16c-91e83ecbd13a",  # Opcional
                    # URL do avatar, # Opcional
                    "avatar": "https://seu-bucket.s3.amazonaws.com/caminho/para/avatar.jpg",
                    "profit": "0.0",
                },

                request_only=True,
            ),
            OpenApiExample(
                "Exemplo de Resposta (Sucesso)",
                value={
                    "message": "Usuário registrado com sucesso!",
                    "user": {
                        "uid": "7c0fa97f-89d8-427f-a54a-ee9409ce0acb",
                        "name": "João Gomes",
                        "email": "joao.gomes1@gmail.com",
                        "avatar": None
                    },
                    "require_email_confirmation": True
                },
                response_only=True,
            ),
            OpenApiExample(
                "Exemplo de Resposta (Erro - Dados inválidos)",
                value={
                    "email": ["Este campo é obrigatório."],
                    "password": ["As senhas não coincidem."],
                    "cpf": ["CPF inválido."],
                    "plan_uid": ["Plano não encontrado."],
                    "avatar": ["URL inválida para o avatar."]
                },
                response_only=True,
            ),
        ],
    )
)

user_profile_view_schema = extend_schema_view(
    get=extend_schema(
        summary="Visualizar o perfil do usuário autenticado",
        description="Endpoint para visualizar o perfil do usuário autenticado, incluindo informações como nome, email, CPF, avatar e plano ativo.",
        tags=["Usuários"],
        responses={
            200: UserProfileSerializer,  # Vincula o serializer correto

        },
        examples=[
            OpenApiExample(
                "Exemplo de Resposta (Sucesso)",
                value={
                    "uid": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "cpf": "12345678901",
                    "avatar": "https://seu-bucket.s3.amazonaws.com/caminho/para/avatar.jpg",
                    "date_joined": "2025-03-25T12:00:00Z",
                    "profit": "0.0",
                    "active_plan": {
                        "id": 1,
                        "uid": "plan-uid-123",
                        "name": "Plano Premium",
                        "description": "Acesso completo",
                        "price": 99.99,
                        "duration": "Mensal",
                        "duration_value": 30
                    }
                },
                response_only=True,
            ),
        ],
    ),
    put=extend_schema(
        summary="Atualizar o perfil do usuário autenticado",
        description="Endpoint para atualizar o perfil do usuário autenticado. O campo `avatar` pode ser atualizado para alterar a imagem de avatar.",
        tags=["Usuários"],
        request=UserProfileSerializer,
        responses={
            200: UserProfileSerializer,  # Vincula o serializer correto

        },
        examples=[
            OpenApiExample(
                "Exemplo de Requisição",
                value={
                    "name": "John Doe",
                    "avatar": "https://seu-bucket.s3.amazonaws.com/caminho/para/avatar.jpg"
                },
                request_only=True,
            ),
            OpenApiExample(
                "Exemplo de Resposta (Sucesso)",
                value={
                    "uid": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "cpf": "12345678901",
                    "avatar": "https://seu-bucket.s3.amazonaws.com/caminho/para/avatar.jpg",
                    "date_joined": "2025-03-25T12:00:00Z",
                    "profit": "0.0",
                    "active_plan": {
                        "id": 1,
                        "uid": "plan-uid-123",
                        "name": "Plano Premium",
                        "description": "Acesso completo",
                        "price": 99.99,
                        "duration": "Mensal",
                        "duration_value": 30
                    }
                },
                response_only=True,
            ),
        ],
    )
)

change_password_view_schema = extend_schema_view(
    post=extend_schema(
        request=ChangePasswordSerializer,
        responses={200: ChangePasswordSerializer},
        description="Endpoint para alterar a senha do usuário autenticado."
    )
)


login_view_schema = extend_schema_view(
    post=extend_schema(
        request=LoginSerializer,
        responses={200: LoginSerializer},
        description="Endpoint para login."
    )
)

logout_view_schema = extend_schema_view(
    post=extend_schema(
        description="Endpoint para logout.",
        responses={205: None}
    )
)


upload_avatar_view_schema = extend_schema_view(
    post=extend_schema(
        summary="Fazer upload do avatar do usuário",
        description=(
            "Endpoint para fazer upload de um avatar para o bucket S3. "
            "O avatar será armazenado no S3 e a URL será salva no perfil do usuário."
        ),
        tags=["Avatar"],
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "avatar": {
                        "type": "string",
                        "format": "binary",
                        "description": "Arquivo de imagem para o avatar (máximo de 10MB)."
                    }
                },
                "required": ["avatar"]
            }
        },
        responses={
            200: OpenApiExample(
                "Sucesso",
                value={
                    "message": "Avatar enviado com sucesso.",
                    "avatar_url": "https://your_bucket_name.s3.your_region.amazonaws.com/avatars/<user_uid>/<file_name>"
                },
                response_only=True,
            ),
            400: OpenApiExample(
                "Erro - Nenhum arquivo enviado",
                value={
                    "error": "Nenhum arquivo enviado."
                },
                response_only=True,
            ),
            400: OpenApiExample(
                "Erro - Arquivo muito grande",
                value={
                    "error": "O arquivo excede o tamanho máximo permitido de 10MB."
                },
                response_only=True,
            ),
            500: OpenApiExample(
                "Erro - Problema com o S3",
                value={
                    "error": "Erro ao fazer upload do avatar: <detalhes do erro>"
                },
                response_only=True,
            ),
        },
        examples=[
            OpenApiExample(
                "Exemplo de Requisição",
                value={
                    "avatar": "(arquivo de imagem enviado via form-data)"
                },
                request_only=True,
            ),
            OpenApiExample(
                "Exemplo de Resposta (Sucesso)",
                value={
                    "message": "Avatar enviado com sucesso.",
                    "avatar_url": "https://your_bucket_name.s3.your_region.amazonaws.com/avatars/<user_uid>/<file_name>"
                },
                response_only=True,
            ),
            OpenApiExample(
                "Exemplo de Resposta (Erro - Nenhum arquivo enviado)",
                value={
                    "error": "Nenhum arquivo enviado."
                },
                response_only=True,
            ),
            OpenApiExample(
                "Exemplo de Resposta (Erro - Arquivo muito grande)",
                value={
                    "error": "O arquivo excede o tamanho máximo permitido de 10MB."
                },
                response_only=True,
            ),
        ],
    )
)


create_user_view_schema = extend_schema(
    summary="Criar um novo usuário",
    description="Permite que administradores criem novos usuários. O campo 'admin' é opcional e define se o usuário será administrador.",
    examples=[
        OpenApiExample(
            "Exemplo de criação de usuário administrador",
            value={
                "email": "pedro@gmail.com",
                "cpf": "97805704031",
                "name": "Pedro Almeida",
                "password": "Password123!",
                "confirm_password": "Password123!",
                "admin": True
            },
            request_only=True,  # Este exemplo é apenas para a requisição
        ),
        OpenApiExample(
            "Resposta de sucesso",
            value={
                "message": "Usuário criado com sucesso.",
                "user": {
                    "uid": "b77d099a-8577-4e93-b213-7e95884b16bd",
                    "name": "Pedro Almeida",
                    "email": "pedro@gmail.com",
                    "is_admin": True
                }
            },
            response_only=True,  # Este exemplo é apenas para a resposta
        ),
    ],
)

multiple_delete_schema = extend_schema(
    summary="Excluir Múltiplos Usuários",
    description="Permite que administradores excluam múltiplos usuários com base em uma lista de UIDs.",
    request=MultipleDeleteSerializer,
    examples=[
        OpenApiExample(
            "Exemplo de Requisição",
            value={
                "uids": [
                    "0f10470f-90bb-4281-8928-91a31a84e78c",
                    "1a20470f-90bb-4281-8928-91a31a84e78d"
                ]
            },
            request_only=True,
        ),
        OpenApiExample(
            "Exemplo de Resposta",
            value={"message": "2 usuário(s) excluído(s) com sucesso."},
            response_only=True,
        ),
    ],
)

password_reset_request_schema = extend_schema(
    summary="Solicitar recuperação de senha",
    description="Envia um código de recuperação para o e-mail informado.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email", "example": "usuario@email.com"}
            },
            "required": ["email"]
        }
    },
    responses={
        200: OpenApiTypes.OBJECT,

    },
    examples=[
        OpenApiExample(
            "Exemplo de solicitação",
            value={"email": "usuario@email.com"},
            request_only=True,
        ),
        OpenApiExample(
            "Exemplo de resposta de sucesso",
            value={"message": "Código de recuperação enviado com sucesso."},
            response_only=True,
        ),
        OpenApiExample(
            "Exemplo de resposta de erro",
            value={"error": "Usuário não encontrado."},
            response_only=True,
        ),
    ]
)

password_reset_confirm_schema = extend_schema(
    summary="Confirmar código de recuperação e redefinir senha",
    description="Confirma o código de recuperação e redefine a senha do usuário.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email", "example": "usuario@email.com"},
                "recovery_code": {"type": "string", "example": "123456"},
                "new_password": {"type": "string", "example": "NovaSenhaForte123"},
                "confirm_password": {"type": "string", "example": "NovaSenhaForte123"}
            },
            "required": ["email", "recovery_code", "new_password", "confirm_password"]
        }
    },
    responses={
        200: OpenApiTypes.OBJECT,

    },
    examples=[
        OpenApiExample(
            "Exemplo de solicitação",
            value={
                "email": "usuario@email.com",
                "recovery_code": "123456",
                "new_password": "NovaSenhaForte123",
                "confirm_password": "NovaSenhaForte123"
            },
            request_only=True,
        ),
        OpenApiExample(
            "Exemplo de resposta de sucesso",
            value={"message": "Senha redefinida com sucesso."},
            response_only=True,
        ),
        OpenApiExample(
            "Exemplo de resposta de erro",
            value={"error": "Código de recuperação inválido ou expirado."},
            response_only=True,
        ),
    ]
)
