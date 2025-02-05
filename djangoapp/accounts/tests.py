from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer

User = get_user_model()


class AuthenticationTests(APITestCase):
    def create_user(self, email, cpf, password, is_admin=False):
        """Função auxiliar para criar usuários de forma reutilizável."""
        user_data = {
            "email": email,
            "cpf": cpf,
            "password": password,
            "confirm_password": password,
            "name": "Usuário Teste" if not is_admin else "Administrador",
        }
        serializer = RegisterSerializer(data=user_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        if is_admin:
            user.is_superuser = True
            user.is_staff = True
            user.save()
        return user

    def authenticate_admin(self):
        """Autentica o admin e armazena o token."""
        login_url = reverse("login")
        login_data = {"identifier": self.admin_user.email,
                      "password": "Admin@123"}
        response = self.client.post(login_url, login_data, format="json")

        if response.status_code != status.HTTP_200_OK or "access" not in response.data:
            self.fail(f"Falha ao autenticar admin: {response.data}")

        self.admin_token = response.data["access"]
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

    def setUp(self):
        """Criação de usuários e autenticação do admin."""
        self.user = self.create_user(
            "test@example.com", "97359116040", "Senha@123")
        self.admin_user = self.create_user(
            "admin@example.com", "57885953041", "Admin@123", is_admin=True)
        self.authenticate_admin()

    def test_register_user(self):
        """Testa o registro de um novo usuário."""
        data = {
            "email": "newuser@example.com",
            "cpf": "30740665049",
            "password": "Newpassword1!",
            "confirm_password": "Newpassword1!",
            "name": "New User",
        }
        response = self.client.post(
            reverse("account-create-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                         f"Erro no registro: {response.data}")
        self.assertEqual(User.objects.count(), 3,
                         "Usuário não foi criado corretamente.")

    def test_login_user(self):
        """Testa login com credenciais válidas."""
        data = {"identifier": self.user.email, "password": "Senha@123"}
        response = self.client.post(reverse("login"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         f"Erro no login: {response.data}")
        self.assertIn("access", response.data,
                      "Token de acesso não retornado.")
        self.assertIn("refresh", response.data,
                      "Token de refresh não retornado.")

    def test_logout_user(self):
        """Testa o logout de um usuário autenticado."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        response = self.client.post(
            reverse("logout"), {"refresh": str(refresh)}, format="json")
        self.assertIn(response.status_code, [
                      status.HTTP_200_OK, status.HTTP_205_RESET_CONTENT], f"Erro no logout: {response.data}")
        self.assertEqual(response.data.get(
            "message"), "Logout realizado com sucesso!", "Mensagem de logout incorreta.")

    def test_list_users_admin_only(self):
        """Verifica que apenas admins podem listar usuários."""
        # Usuário comum deve receber 403
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(RefreshToken.for_user(self.user).access_token)}')
        response = self.client.get(reverse("user-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         "Usuário comum conseguiu acessar lista de usuários.")

        # Admin deve receber 200
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.get(reverse("user-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         f"Erro ao listar usuários como admin: {response.data}")

    def test_token_refresh(self):
        """Testa se o refresh token gera um novo access token."""
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post(reverse("token_refresh"), {
                                    "refresh": str(refresh)}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         f"Erro ao renovar token: {response.data}")
        self.assertIn("access", response.data,
                      "Novo token de acesso não gerado.")

    def test_token_verify(self):
        """Testa a verificação de um token de acesso válido."""
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post(reverse("token_verify"), {
                                    "token": str(refresh.access_token)}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         f"Erro ao verificar token: {response.data}")

    def test_filter_users(self):
        """Testa a filtragem de usuários na listagem (apenas admin)."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.get(reverse("filter-users") + "?search=test")
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         f"Erro na filtragem de usuários: {response.data}")
        self.assertGreaterEqual(len(response.data.get(
            "results", [])), 1, "Nenhum usuário encontrado na filtragem.")





