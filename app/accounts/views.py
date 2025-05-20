from rest_framework.views import APIView
from rest_framework import viewsets, status, filters
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, UpdateUserPlanSerializer, UserProfileSerializer, ChangePasswordSerializer, UserSubscriptionSerializer, PlanSerializer, MultipleDeleteSerializer, AdminUserUpdateSerializer
from rest_framework.decorators import action
from django.utils.crypto import get_random_string
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
import logging
from .models import Usuario, LoginLog
from payments.models import UserSubscription
from rest_framework_simplejwt.tokens import RefreshToken
import user_agents
import uuid
from django.utils import timezone
from django.conf import settings
from .permissions import IsAdminUserForList
import os
import boto3
from datetime import timedelta
from datetime import datetime
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, BotoCoreError, ClientError
from .schema import (
    register_view_schema, user_profile_view_schema, change_password_view_schema,
    login_view_schema, logout_view_schema,
    update_user_plan_view_schema, user_plan_view_schema, user_subscription_history_view_schema, upload_avatar_view_schema, create_user_view_schema, multiple_delete_schema
)

logger = logging.getLogger('django')


@register_view_schema
class RegisterView(APIView):
    """
    View para registrar um novo usuário.
    """

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Verificar se a confirmação de e-mail é necessária
            require_email_confirmation = os.getenv(
                "REQUIRE_EMAIL_CONFIRMATION", "True") == "False"

            # Gerar tokens JWT
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Adicionar todas as chaves esperadas na resposta
            response_data = {
                "message": "Usuário registrado com sucesso!",
                "user": {
                    "uid": str(user.uid),
                    "name": user.name,
                    "email": user.email,
                    "cpf": user.cpf,
                    "avatar": user.avatar.url if user.avatar else None,
                    "date_joined": user.date_joined.isoformat(),
                },
                "require_email_confirmation": require_email_confirmation,
                "refresh": str(refresh),
                "access": access_token,
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@user_profile_view_schema
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
        if not serializer.is_valid():
            # Retorna 400 com os erros de validação
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@change_password_view_schema
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


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar usuários.
    """
    queryset = Usuario.objects.all().order_by("uid")
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['date_joined']
    ordering = ['-date_joined']
    search_fields = ['name', 'email']
    lookup_field = 'uid'
    permission_classes = [IsAdminUserForList]

    def get_serializer_class(self):
        """
        Define o serializer baseado na ação.
        """
        if self.action == 'list':
            return UserProfileSerializer
        elif self.action == 'retrieve':
            return UserProfileSerializer
        elif self.action in ['update', 'partial_update']:
            return AdminUserUpdateSerializer
        elif self.action == 'create':
            return RegisterSerializer
        return super().get_serializer_class()

    @create_user_view_schema
    def create(self, request, *args, **kwargs):
        """
        Permite que administradores criem novos usuários.
        O campo 'admin' é opcional e define se o usuário será administrador.
        """
        if not request.user.is_superuser:
            raise PermissionDenied(
                "Apenas administradores podem criar usuários.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password = serializer.validated_data.get("password")
        confirm_password = request.data.get("confirm_password")
        if password != confirm_password:
            return Response(
                {"detail": "As senhas não coincidem."},
                status=status.HTTP_400_BAD_REQUEST
            )

        admin_flag = request.data.get("admin", False)
        user = Usuario.objects.create_user(
            email=serializer.validated_data["email"],
            cpf=serializer.validated_data["cpf"],
            name=serializer.validated_data["name"],
            password=password,
        )

        if admin_flag:
            user.is_superuser = True
            user.save()

        return Response(
            {
                "message": "Usuário criado com sucesso.",
                "user": {
                    "uid": user.uid,
                    "name": user.name,
                    "email": user.email,
                    "is_admin": user.is_superuser,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    def list(self, request, *args, **kwargs):
        """
        Lista todos os usuários (apenas para administradores).
        """
        queryset = self.filter_queryset(self.get_queryset())

        if not queryset.exists():
            return Response(
                {"count": 0, "detail": "Nenhum usuário encontrado.", "results": []},
                status=status.HTTP_200_OK
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_superuser and instance != request.user:
            raise PermissionDenied(
                "Você não tem permissão para acessar este recurso.")
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        Atualiza os dados do usuário.
        """
        partial = kwargs.pop(
            'partial', False)
        instance = self.get_object()

        if not request.data:
            return Response(
                {"detail": "Nenhum dado foi enviado para atualização."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Salva as alterações no usuário
        serializer.save()

        return Response(
            {"detail": "Alteração feita com sucesso.", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied(
                "Apenas administradores podem deletar usuários.")
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Usuário excluído com sucesso."},
            status=status.HTTP_200_OK
        )

    @multiple_delete_schema
    @action(detail=False, methods=['post'], url_path='multiple-delete', permission_classes=[IsAdminUserForList])
    def multiple_delete(self, request, *args, **kwargs):
        """
        Exclui múltiplos usuários com base em uma lista de UIDs.
        """
        serializer = MultipleDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uids = serializer.validated_data['uids']
        users_to_delete = Usuario.objects.filter(uid__in=uids)

        if not users_to_delete.exists():
            return Response(
                {"detail": "Nenhum usuário encontrado com os UIDs fornecidos."},
                status=status.HTTP_404_NOT_FOUND
            )

        count = users_to_delete.count()
        users_to_delete.delete()

        return Response(
            {"message": f"{count} usuário(s) excluído(s) com sucesso."},
            status=status.HTTP_200_OK
        )


@login_view_schema
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


@logout_view_schema
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


@upload_avatar_view_schema
class UploadAvatarView(APIView):
    """
    Endpoint para fazer upload do avatar para o bucket S3.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        avatar_file = request.FILES.get('avatar')
        if not avatar_file:
            return Response({"error": "Nenhum arquivo enviado."}, status=status.HTTP_400_BAD_REQUEST)

        # Valida o tamanho do arquivo (10MB)
        max_size_mb = 10
        if avatar_file.size > max_size_mb * 1024 * 1024:
            return Response(
                {"error": f"O arquivo excede o tamanho máximo permitido de {max_size_mb}MB."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Configura o cliente S3
        try:
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_DEFAULT_REGION
            )
        except Exception as e:
            return Response(
                {"error": f"Erro ao configurar o cliente S3: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Verifica se as configurações do S3 estão corretas
        if not settings.AWS_BUCKET or not settings.AWS_DEFAULT_REGION:
            return Response(
                {"error": "Configurações do AWS S3 estão ausentes ou inválidas."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Define o caminho do arquivo no bucket com data e nome aleatório
        avatar_folder = "avatars/"
        # Data e hora no formato YYYYMMDDHHMMSS
        current_date = datetime.now().strftime("%Y%m%d%H%M%S")
        # Nome com data e extensão original
        random_filename = f"{current_date}_{uuid.uuid4().hex}{os.path.splitext(avatar_file.name)[1]}"
        file_path = f"{avatar_folder}{request.user.uid}/{random_filename}"

        try:
            # Faz o upload do arquivo para o S3
            s3.upload_fileobj(
                avatar_file,
                settings.AWS_BUCKET,
                file_path,
                ExtraArgs={'ContentType': avatar_file.content_type,
                           'ACL': 'public-read'}
            )

            # Gera a URL pública do arquivo
            avatar_url = f"https://{settings.AWS_BUCKET}.s3.{settings.AWS_DEFAULT_REGION}.amazonaws.com/{file_path}"

            # Atualiza o campo avatar do usuário
            request.user.avatar = avatar_url
            request.user.save()

            return Response(
                {"message": "Avatar enviado com sucesso.", "avatar_url": avatar_url},
                status=status.HTTP_200_OK
            )
        except (NoCredentialsError, PartialCredentialsError):
            return Response(
                {"error": "Erro de credenciais do AWS S3. Verifique as configurações."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {"error": f"Erro ao fazer upload do avatar: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PasswordResetRequestView(APIView):
    """
    Endpoint para solicitar a recuperação de senha.
    Envia um código de recuperação por e-mail usando AWS SES.
    """

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "O campo 'email' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar se o e-mail está associado a um usuário
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return Response({"error": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Gerar um código de recuperação
        recovery_code = get_random_string(length=6, allowed_chars="0123456789")

        # Salvar o código no cache com validade de X minutos
        cache_key = f"password_reset_{user.uid}"
        cache.set(cache_key, recovery_code, timeout=timedelta(
            minutes=10).total_seconds())  # Código válido por 10 minutos

        # Configurar o cliente SES
        ses_client = boto3.client(
            'ses',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION
        )

        # Enviar o e-mail com o código de recuperação
        try:
            ses_client.send_email(
                Source=settings.AWS_SES_SOURCE_EMAIL,
                Destination={"ToAddresses": [email]},
                Message={
                    "Subject": {"Data": "Recuperação de Senha"},
                    "Body": {
                        "Text": {
                            "Data": f"Olá {user.name},\n\nSeu código de recuperação de senha é: {recovery_code}\n\nEste código é válido por 10 minutos."
                        }
                    }
                }
            )
        except (BotoCoreError, ClientError) as e:
            return Response({"error": f"Erro ao enviar o e-mail: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Código de recuperação enviado com sucesso."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    Endpoint para confirmar o código de recuperação e redefinir a senha.
    """

    def post(self, request):
        email = request.data.get("email")
        recovery_code = request.data.get("recovery_code")
        new_password = request.data.get("new_password")

        if not email or not recovery_code or not new_password:
            return Response({"error": "Os campos 'email', 'recovery_code' e 'new_password' são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar se o e-mail está associado a um usuário
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return Response({"error": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Verificar o código de recuperação no cache
        cache_key = f"password_reset_{user.uid}"
        cached_code = cache.get(cache_key)

        if not cached_code or cached_code != recovery_code:
            return Response({"error": "Código de recuperação inválido ou expirado."}, status=status.HTTP_400_BAD_REQUEST)

        # Atualizar a senha do usuário
        user.set_password(new_password)
        user.save()

        # Remover o código do cache
        cache.delete(cache_key)

        return Response({"message": "Senha redefinida com sucesso."}, status=status.HTTP_200_OK)
