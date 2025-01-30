
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
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
    queryset = Usuario.objects.all()
    serializer_class = RegisterSerializer
    pagination_class = StandardResultsSetPagination # Usando a paginação personalizada


class AccountRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    View para detalhar, atualizar ou excluir a conta do usuário.
    Permite buscar o usuário pelo ID na URL.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Usuario.objects.all()
    serializer_class = RegisterSerializer

    def get_object(self):
        """
        Sobrescreve o método para buscar o usuário pelo ID fornecido na URL.
        """
        user_id = self.kwargs.get("pk")  # Obtém o ID da URL
        try:
            return Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            raise ValidationError({"error": "Usuário não encontrado."})

    def update(self, request, *args, **kwargs):
        """
        Lida com PUT para atualização completa ou PATCH para atualização parcial.
        """
        user = self.get_object()
        data = request.data

        allowed_fields = ['name', 'email', 'password']  # Campos permitidos
        updated_fields = {}

        for field in allowed_fields:
            if field in data:
                updated_fields[field] = data[field]

        if not updated_fields:
            return Response(
                {"error": "Nenhum campo válido foi fornecido para atualização."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Atualiza os campos fornecidos
        for field, value in updated_fields.items():
            if field == 'password':  # Trate o password separadamente
                user.set_password(value)
            else:
                setattr(user, field, value)

        user.save()

        return Response(
            {
                "message": "Usuário atualizado com sucesso.",
                "updated_fields": updated_fields,
            },
            status=status.HTTP_200_OK,
        )


class FilterUsersView(generics.ListAPIView):
    """
    View para listar, filtrar, pesquisar e ordenar usuários.
    - Suporte a múltiplos tipos de filtros: exato, intervalo, pesquisa e ordenação.
    - Paginada para lidar com grandes quantidades de dados.
    """
    permission_classes = [IsAuthenticated]
    queryset = Usuario.objects.all()
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
