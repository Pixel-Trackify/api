
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.exceptions import TokenError
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, UserUpdateSerializer, UpdateUserPlanSerializer, UserProfileSerializer, ChangePasswordSerializer, UserSubscriptionSerializer, PlanSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import NotFound
from rest_framework import generics
import logging
from .models import Usuario, LoginLog
from plans.models import Plan, UserSubscription
from .filters import UsuarioFilter
import user_agents
from django.utils import timezone


class RegisterView(APIView):
    """
    View para registrar um novo usuário.
    """

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Usuário registrado com sucesso!",
                "user": {
                    "uid": user.uid,
                    "name": user.name,
                    "email": user.email
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """
    Endpoint para visualizar e atualizar o perfil do usuário autenticado.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(
            request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(APIView):
    """
    Endpoint para alterar a senha do usuário autenticado.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({"message": "Senha alterada com sucesso."}, status=status.HTTP_200_OK)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class GetUsersView(generics.ListAPIView):
    # Apenas administradores podem listar usuários
    permission_classes = [IsAdminUser]
    queryset = Usuario.objects.all().order_by("uid")
    serializer_class = RegisterSerializer
    # Usando a paginação personalizada
    pagination_class = StandardResultsSetPagination


class AccountRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    View para detalhar, atualizar ou excluir a conta do usuário.
    Requer autenticação para edição e só permite que o dono da conta edite.
    """
    permission_classes = [
        IsAuthenticated]  # Exige autenticação para todas as ações exceto GET?
    queryset = Usuario.objects.all()
    # Serializador específico para atualização
    serializer_class = UserUpdateSerializer
    lookup_field = 'uid'  # Campo para busca de usuário na URL

    def get_object(self):
        """Busca o usuário pelo ID na URL e verifica permissões."""
        user_uid = self.kwargs.get("pk")
        try:
            user = Usuario.objects.get(uid=user_uid)
        except Usuario.DoesNotExist:
            raise NotFound(detail="Usuário não encontrado.",
                           code="not_found")  # HTTP 404

        # Verifica se o usuário autenticado é o dono do recurso
        if self.request.user != user:
            # Esconde a existência do recurso para não donos
            raise NotFound(detail="Usuário não encontrado.")

        return user

    def update(self, request, *args, **kwargs):
        """Atualização parcial (PATCH) ou total (PUT) usando o serializer."""
        user = self.get_object()
        serializer = self.get_serializer(
            instance=user, data=request.data, partial=bool(request.method == 'PATCH'))
        serializer.is_valid(raise_exception=True)

        # Salva alterações (incluindo tratamento de password pelo serializer)
        serializer.save()

        return Response(
            {
                "message": "Usuário atualizado com sucesso.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK
        )


class FilterUsersView(generics.ListAPIView):
    """
    View para listar, filtrar, pesquisar e ordenar usuários.
    - Suporte a múltiplos tipos de filtros: exato, intervalo, pesquisa e ordenação.
    - Paginada para lidar com grandes quantidades de dados.
    """
    permission_classes = [IsAuthenticated]
    queryset = Usuario.objects.all().order_by("uid")
    serializer_class = RegisterSerializer
    pagination_class = StandardResultsSetPagination

    # Configuração dos backends de filtro, pesquisa e ordenação
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UsuarioFilter  # Filtros personalizados
    search_fields = ['name', 'email']  # Campos para pesquisa textual
    ordering_fields = ['name', 'email', 'created_at']  # Ordenação permitida
    # ordering = ['id']  # Ordenação padrão


logger = logging.getLogger('accounts')  # Logger para a aplicação de accounts


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        # Verificar se o usuário está ativo
        if not user.is_active:
            return Response({"error": "Conta inativa ou bloqueada"}, status=status.HTTP_403_FORBIDDEN)

        # Verificar se o e-mail está confirmado (se necessário)
        '''email_address = user.emailaddress_set.filter(email=user.email).first()
        if not email_address or not email_address.verified:
            return Response({"error": "Email não verificado"}, status=status.HTTP_400_BAD_REQUEST)'''

        # Gerar tokens JWT
        refresh = RefreshToken.for_user(user)

        # Registrar o log de login
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        user_agent = user_agents.parse(user_agent_string)
        device = f"{user_agent.device.family} {user_agent.device.brand} {user_agent.device.model}"
        browser = f"{user_agent.browser.family} {user_agent.browser.version_string}"
        token = str(refresh.access_token)

        LoginLog.objects.create(
            user=user,
            ip_address=ip_address,
            device=device,
            browser=browser,
            login_time=timezone.now(),
            token=token
        )

        logger.info(f"Usuário {user.email} logado com sucesso.")

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    # Apenas usuários autenticados podem fazer logout
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Obtém o token de refresh do corpo da requisição
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                logger.warning("Tentativa de logout sem token de refresh.")
                return Response(
                    {"error": "O campo 'refresh' é obrigatório."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Tenta invalidar o token de refresh
            token = RefreshToken(refresh_token)
            token.blacklist()  # Adiciona o token à lista negra

            # Registra o logout no logger
            user = request.user
            logger.info(f"Usuário {user.name} fez logout com sucesso.")

            return Response(
                {"message": "Logout realizado com sucesso!"},
                status=status.HTTP_205_RESET_CONTENT
            )
        except TokenError as e:
            # Captura erros relacionados ao token (ex.: token inválido ou expirado)
            logger.error(f"Erro durante o logout: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Captura outros erros inesperados
            logger.error(f"Erro inesperado durante o logout: {str(e)}")
            return Response(
                {"error": "Ocorreu um erro durante o logout."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateUserPlanView(APIView):
    """
    Endpoint para atualizar o plano do usuário autenticado.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = UpdateUserPlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(request.user, serializer.validated_data)
        return Response({"message": "Plano atualizado com sucesso."}, status=status.HTTP_200_OK)


class UserPlanView(APIView):
    """Retorna o plano do usuário autenticado"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscription = request.user.subscriptions.filter(
            is_active=True).first()
        if not subscription:
            return Response({"message": "Nenhum plano ativo encontrado."}, status=404)

        plan_data = PlanSerializer(subscription.plan).data


class UserSubscriptionHistoryView(APIView):
    """
    Retorna o histórico de assinaturas do usuário autenticado.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscriptions = UserSubscription.objects.filter(user=request.user)
        serializer = UserSubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)
