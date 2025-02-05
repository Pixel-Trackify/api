
from rest_framework.views import APIView
from django.http import Http404
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, UserUpdateSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import NotFound
from rest_framework import generics
import logging
from .models import Usuario
from .filters import UsuarioFilter


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
                    "id": user.id,
                    "name": user.name,
                    "email": user.email
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class GetUsersView(generics.ListAPIView):
    permission_classes = [IsAdminUser] # Apenas administradores podem listar usuários
    queryset = Usuario.objects.all().order_by("id")
    serializer_class = RegisterSerializer
    pagination_class = StandardResultsSetPagination # Usando a paginação personalizada


class AccountRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    View para detalhar, atualizar ou excluir a conta do usuário.
    Requer autenticação para edição e só permite que o dono da conta edite.
    """
    permission_classes = [
        IsAuthenticated]  # Exige autenticação para todas as ações exceto GET?
    queryset = Usuario.objects.all().order_by("id")
    serializer_class = UserUpdateSerializer # Serializador específico para atualização

    def get_object(self):
        """Busca o usuário pelo ID na URL e verifica permissões."""
        user_id = self.kwargs.get("pk")
        try:
            user = Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            raise NotFound(detail="Usuário não encontrado.",
                           code="not_found")  # HTTP 404

        # Verifica se o usuário autenticado é o dono do recurso
        if self.request.user != user:
            raise NotFound(detail="Usuário não encontrado.") # Esconde a existência do recurso para não donos

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
    queryset = Usuario.objects.all().order_by("id")
    serializer_class = RegisterSerializer
    pagination_class = StandardResultsSetPagination

    # Configuração dos backends de filtro, pesquisa e ordenação
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UsuarioFilter  # Filtros personalizados
    search_fields = ['name', 'email']  # Campos para pesquisa textual
    ordering_fields = ['name', 'email', 'created_at']  # Ordenação permitida
    #ordering = ['id']  # Ordenação padrão


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
       
            if not email_address or not email_address.verified:
                return Response({"error": "Email não verificado"}, status=status.HTTP_400_BAD_REQUEST)

        # Gerar tokens JWT
        refresh = RefreshToken.for_user(user)

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
