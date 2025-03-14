from drf_spectacular.utils import extend_schema, extend_schema_view
from .serializers import RegisterSerializer, UserProfileSerializer, ChangePasswordSerializer, UserUpdateSerializer, UpdateUserPlanSerializer, PlanSerializer, UserSubscriptionSerializer, LoginSerializer

register_view_schema = extend_schema_view(
    post=extend_schema(
        request=RegisterSerializer,
        responses={201: RegisterSerializer},
        description="Endpoint para registrar um novo usuário."
    )
)

user_profile_view_schema = extend_schema_view(
    get=extend_schema(
        request=UserProfileSerializer,
        responses={200: UserProfileSerializer},
        description="Endpoint para visualizar o perfil do usuário autenticado."
    ),
    put=extend_schema(
        request=UserProfileSerializer,
        responses={200: UserProfileSerializer},
        description="Endpoint para atualizar o perfil do usuário autenticado."
    )
)

change_password_view_schema = extend_schema_view(
    post=extend_schema(
        request=ChangePasswordSerializer,
        responses={200: ChangePasswordSerializer},
        description="Endpoint para alterar a senha do usuário autenticado."
    )
)

get_users_view_schema = extend_schema_view(
    get=extend_schema(
        description="Endpoint para listar usuários. Apenas administradores podem acessar.",
        responses={200: UserProfileSerializer(many=True)}
    )
)

account_retrieve_update_destroy_view_schema = extend_schema_view(
    get=extend_schema(
        description="Endpoint para detalhar a conta do usuário.",
        responses={200: UserUpdateSerializer}
    ),
    put=extend_schema(
        request=UserUpdateSerializer,
        responses={200: UserUpdateSerializer},
        description="Endpoint para atualizar a conta do usuário."
    ),
    delete=extend_schema(
        description="Endpoint para excluir a conta do usuário.",
        responses={204: None}
    )
)

filter_users_view_schema = extend_schema_view(
    get=extend_schema(
        description="Endpoint para listar, filtrar, pesquisar e ordenar usuários.",
        responses={200: RegisterSerializer(many=True)}
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

update_user_plan_view_schema = extend_schema_view(
    post=extend_schema(
        request=UpdateUserPlanSerializer,
        responses={200: UpdateUserPlanSerializer},
        description="Endpoint para atualizar o plano do usuário autenticado."
    )
)

user_plan_view_schema = extend_schema_view(
    get=extend_schema(
        description="Endpoint para retornar o plano do usuário autenticado.",
        responses={200: PlanSerializer}
    )
)

user_subscription_history_view_schema = extend_schema_view(
    get=extend_schema(
        description="Endpoint para retornar o histórico de assinaturas do usuário autenticado.",
        responses={200: UserSubscriptionSerializer(many=True)}
    )
)