from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer

User = get_user_model()


class AuthenticationTests(APITestCase):
    def create_user(self, email, cpf, password, is_admin=False):
        """Cria um usuário e trata exceções."""
        try:
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
        except Exception as e:
            self.fail(f"Erro ao criar usuário: {str(e)}")

    def authenticate_admin(self):
        """Autentica um admin e define o token de autorização."""
        try:
            login_url = reverse("login")
            login_data = {"identifier": self.admin_user.email,
                          "password": "Admin@123"}
            response = self.client.post(login_url, login_data, format="json")

            self.assertEqual(response.status_code, status.HTTP_200_OK,
                             f"Erro no login: {response.data}")
            self.assertIn("access", response.data,
                          "Token de acesso não retornado.")

            self.admin_token = response.data["access"]
            self.client.credentials(
                HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        except Exception as e:
            self.fail(f"Erro na autenticação do admin: {str(e)}")

    def setUp(self):
        """Configuração inicial do ambiente de testes."""
        try:
            self.user = self.create_user(
                "test@example.com", "97359116040", "Senha@123")
            self.admin_user = self.create_user(
                "admin@example.com", "57885953041", "Admin@123", is_admin=True)
            self.authenticate_admin()
        except Exception as e:
            self.fail(f"Erro no setup dos testes: {str(e)}")

    def execute_request(self, method, url, data=None, expected_status=None):
        """Executa requisições e verifica a resposta."""
        try:
            response = getattr(self.client, method)(url, data, format="json")
            expected_status = expected_status or [status.HTTP_200_OK]
            if not isinstance(expected_status, list):
                expected_status = [expected_status]
            self.assertIn(response.status_code, expected_status,
                          f"Erro na requisição: {response.data}")
        except Exception as e:
            self.fail(
                f"Erro ao executar requisição {method.upper()} {url}: {str(e)}")
        return response

    def test_register_user(self):
        """Testa o registro de um novo usuário."""
        data = {
            "email": "newuser@example.com",
            "cpf": "30740665049",
            "password": "Newpassword1!",
            "confirm_password": "Newpassword1!",
            "name": "New User",
        }
        self.execute_request("post", reverse(
            "account-create-list"), data, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3,
                         "Usuário não foi criado corretamente.")

    def test_login_user(self):
        """Testa login com credenciais válidas."""
        data = {"identifier": self.user.email, "password": "Senha@123"}
        response = self.execute_request(
            "post", reverse("login"), data, status.HTTP_200_OK)
        self.assertIn("access", response.data,
                      "Token de acesso não retornado.")

    def test_logout_user(self):
        """Testa o logout de um usuário autenticado."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        response = self.execute_request("post", reverse(
            "logout"), {"refresh": str(refresh)}, expected_status=[200, 205])
        self.assertEqual(response.data.get(
            "message"), "Logout realizado com sucesso!", "Mensagem de logout incorreta.")

    def test_list_users_admin_only(self):
        """Verifica que apenas admins podem listar usuários."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(RefreshToken.for_user(self.user).access_token)}')
        self.execute_request("get", reverse("user-list"),
                             expected_status=status.HTTP_403_FORBIDDEN)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        self.execute_request("get", reverse("user-list"),
                             expected_status=status.HTTP_200_OK)

    def test_token_refresh(self):
        """Testa se o refresh token gera um novo access token."""
        refresh = RefreshToken.for_user(self.user)
        response = self.execute_request("post", reverse("token_refresh"), {
                                        "refresh": str(refresh)}, status.HTTP_200_OK)
        self.assertIn("access", response.data,
                      "Novo token de acesso não gerado.")

    def test_token_verify(self):
        """Testa a verificação de um token de acesso válido."""
        refresh = RefreshToken.for_user(self.user)
        self.execute_request("post", reverse("token_verify"), {
                             "token": str(refresh.access_token)}, status.HTTP_200_OK)

    def test_filter_users(self):
        """Testa a filtragem de usuários na listagem (apenas admin)."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.execute_request("get", reverse(
            "filter-users") + "?search=test", expected_status=status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data.get(
            "results", [])), 1, "Nenhum usuário encontrado na filtragem.")

        def test_login_attempts(self):
            """Testa o bloqueio de login após múltiplas tentativas falhas."""
        login_url = reverse("login")
        login_data = {"identifier": self.user.email, "password": "SenhaErrada"}

        # Fazer 5 tentativas de login com senha errada
        for _ in range(5):
            response = self.client.post(login_url, login_data, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verificar se o usuário está bloqueado
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_locked(),
                        "Usuário não foi bloqueado após 5 tentativas falhas.")

        # Tentar fazer login com a senha correta enquanto bloqueado
        login_data["password"] = "Senha@123"
        response = self.client.post(login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         "Usuário conseguiu fazer login enquanto bloqueado.")

        # Simular a passagem do tempo para desbloquear o usuário
        self.user.locked_until = timezone.now() - timedelta(minutes=1)
        self.user.save()

        # Tentar fazer login com a senha correta após o desbloqueio
        response = self.client.post(login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         f"Erro no login: {response.data}")

        # Verificar se o bloqueio foi resetado
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_locked(),
                         "Usuário não foi desbloqueado após login bem-sucedido.")
        self.assertEqual(self.user.login_attempts, 0,
                         "Tentativas de login não foram resetadas após login bem-sucedido.")

    def test_view_profile(self):
        """Testa a visualização do perfil do usuário autenticado."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(RefreshToken.for_user(self.user).access_token)}')
        response = self.execute_request("get", reverse(
            "profile"), expected_status=status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['name'], self.user.name)
        self.assertEqual(response.data['cpf'], self.user.cpf)

    def test_update_profile(self):
        """Testa a atualização do perfil do usuário autenticado."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(RefreshToken.for_user(self.user).access_token)}')
        response = self.execute_request("put", reverse("profile"), {
            'name': 'Updated User',
            'email': 'updated@example.com'
        }, expected_status=status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated User')
        self.assertEqual(response.data['email'], 'updated@example.com')

    def test_change_password(self):
        """Testa a mudança de senha do usuário autenticado."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(RefreshToken.for_user(self.user).access_token)}')
        response = self.execute_request("post", reverse("change_password"), {
            'old_password': 'Senha@123',
            'new_password': 'NewPassword123!',
            'confirm_new_password': 'NewPassword123!'
        }, expected_status=status.HTTP_200_OK)
        self.assertEqual(response.data['message'],
                         'Senha alterada com sucesso.')

    def test_change_password_with_invalid_old_password(self):
        """Testa a mudança de senha com uma senha antiga inválida."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(RefreshToken.for_user(self.user).access_token)}')
        response = self.execute_request("post", reverse("change_password"), {
            'old_password': 'WrongPassword123!',
            'new_password': 'NewPassword123!',
            'confirm_new_password': 'NewPassword123!'
        }, expected_status=status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['old_password']
                         [0], 'Senha antiga incorreta.')

    def test_change_password_with_mismatched_new_passwords(self):
        """Testa a mudança de senha com senhas novas que não coincidem."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(RefreshToken.for_user(self.user).access_token)}')
        response = self.execute_request("post", reverse("change_password"), {
            'old_password': 'Senha@123',
            'new_password': 'NewPassword123!',
            'confirm_new_password': 'DifferentPassword123!'
        }, expected_status=status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['confirm_new_password'][0], 'As senhas não coincidem.')

    def test_change_password_with_weak_new_password(self):
        """Testa a mudança de senha com uma senha nova fraca."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(RefreshToken.for_user(self.user).access_token)}')
        response = self.execute_request("post", reverse("change_password"), {
            'old_password': 'Senha@123',
            'new_password': 'weakpassword',
            'confirm_new_password': 'weakpassword'
        }, expected_status=status.HTTP_400_BAD_REQUEST)
        self.assertIn('A senha deve conter pelo menos 1 letra maiúscula.',
                      response.data['new_password'][0])
        self.assertIn('A senha deve conter pelo menos 1 caractere especial.',
                      response.data['new_password'][0])
