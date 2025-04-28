from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
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
