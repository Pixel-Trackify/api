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








'''from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer

User = get_user_model()


class AuthenticationTests(APITestCase):
    def setUp(self):
        """Cria usuários através da API para garantir validação"""

        # Dados do usuário comum
        user_data = {
            "email": "test@example.com",
            "cpf": "12345678901",
            "password": "Senha@123",
            "confirm_password": "Senha@123",
            "name": "Usuário Teste"
        }
        serializer = RegisterSerializer(data=user_data)
        # Garante que os dados são válidos
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.user = serializer.save()  # Salva o usuário apenas se validado corretamente

        # Dados do admin
        admin_data = {
            "email": "admin@example.com",
            "cpf": "98765432100",
            "password": "Admin@123",
            "confirm_password": "Admin@123",
            "name": "Administrador"
        }
        serializer = RegisterSerializer(data=admin_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.admin_user = serializer.save()

        # Garante que ele seja superusuário
        self.admin_user.is_superuser = True
        self.admin_user.is_staff = True
        self.admin_user.save()


        # Autenticar o admin para testes que precisam de permissão
        login_url = reverse("login")  # Ajuste conforme necessário
        login_data = {"identifier": "admin@example.com", "password": "Admin@123"}
        login_response = self.client.post(login_url, login_data, format="json")

        if "access" in login_response.data:
            self.admin_token = login_response.data["access"]
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        else:
            print("Erro ao autenticar admin:", login_response.data)

    def test_register_user(self):
        data = {
            "email": "newuser@example.com",
            "cpf": "11122233344",
            "password": "Newpassword1!",
            "confirm_password": "Newpassword1!",
            "name": "New User"
        }
        response = self.client.post(
            reverse("account-create-list"), data, format="json")
        print("Register Response:", response.data)  # Debug
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

    def test_login_user(self):
        data = {"identifier": "test@example.com",
                "password": "Senha@123"}
        response = self.client.post(reverse("login"), data, format="json")
        print("Login Response:", response.data)  # Debug
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_logout_user(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        response = self.client.post(
            reverse("logout"), {"refresh": str(refresh)})
        print("Logout Response:", response.data)  # Debug
        self.assertIn(response.status_code, [
                      status.HTTP_200_OK, status.HTTP_205_RESET_CONTENT])
        self.assertEqual(response.data["message"],
                         "Logout realizado com sucesso!")

    def test_list_users_admin_only(self):
        # Testa acesso de usuário comum (deve ser 403)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(RefreshToken.for_user(self.user).access_token)}')
        response = self.client.get(reverse("user-list"))
        print("User List Response (Regular User):", response.data)  # Debug
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Testa acesso de admin (deve ser 200)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.get(reverse("user-list"))
        print("User List Response (Admin):", response.data)  # Debug
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_refresh(self):
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post(
            reverse("token_refresh"), {"refresh": str(refresh)}, format="json")
        print("Token Refresh Response:", response.data)  # Debug
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_token_verify(self):
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post(
            reverse("token_verify"), {"token": str(refresh.access_token)}, format="json")
        print("Token Verify Response:", response.data)  # Debug
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_users(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.get(reverse("filter-users") + "?search=test")
        print("Filter Users Response:", response.data)  # Debug
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)'''




'''from django.urls import reverse
from rest_framework.test import APITestCase

class UsuarioAPITestCase(APITestCase):
    
    def test_usuario_cpf_invalido(self):
        """Falha ao cadastrar um usuário com CPF inválido"""
        url = reverse("account-create-list")
        data = {
            "email": "apiuser@example.com",
            "cpf": "12345678901",
            "name": "API User",
            "password": "SenhaForte123",
            "confirm_password": "SenhaForte123"
        }
        
        try:
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 400)
        except Exception as e:
            print("Erro no teste de CPF inválido!")
            print("Status Code:", response.status_code if 'response' in locals() else "N/A")
            print("Response Data:", response.data if 'response' in locals() else "N/A")
            print("Exceção:", str(e))
            raise
        
    def test_usuario_provedor_email_invalido(self):
        """Falha ao cadastrar um usuário com provedor de email invalido"""
        url = reverse("account-create-list")
        data = {
            "email": "apiuser@dominioquenaoexiste.com",
            "cpf": "98765432100",
            "name": "API User",
            "password": "SenhaForte@123",
            "confirm_password": "SenhaForte@123"
        }
        
        try:
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 400)
        except Exception as e:
            print("Erro no teste de registro de usuário!")
            print("Status Code:", response.status_code if 'response' in locals() else "N/A")
            print("Response Data:", response.data if 'response' in locals() else "N/A")
            print("Exceção:", str(e))
            raise
        
    def test_usuario_senhas_diferentes(self):
        """Falha ao cadastrar um usuário com senhas diferentes"""
        url = reverse("account-create-list")
        data = {
            "email": "apiuser@dominioquenaoexiste.com",
            "cpf": "98765432100",
            "name": "API User",
            "password": "SenhaForte@123",
            "confirm_password": "SenhaForte@1234"
        }
        
        try:
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 400)
        except Exception as e:
            print("Erro no teste de registro de usuário!")
            print("Status Code:", response.status_code if 'response' in locals() else "N/A")
            print("Response Data:", response.data if 'response' in locals() else "N/A")
            print("Exceção:", str(e))
            raise
    
    def test_usuario_senha_fraca(self):
        """Falha ao cadastrar um usuário com senha fraca"""
        url = reverse("account-create-list")
        data = {
            "email": "apiuser@dominioquenaoexiste.com",
            "cpf": "98765432100",
            "name": "API User",
            "password": "123",
            "confirm_password": "123"
        }
        
        try:
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 400)
        except Exception as e:
            print("Erro no teste de registro de usuário!")
            print("Status Code:", response.status_code if 'response' in locals() else "N/A")
            print("Response Data:", response.data if 'response' in locals() else "N/A")
            print("Exceção:", str(e))
            raise
        
    def test_registro_usuario(self):
        """Testa a criação de um novo usuário via API"""
        url = reverse("account-create-list")
        data = {
            "email": "apiuser@gmail.com",
            "cpf": "98765432100",
            "name": "API User",
            "password": "SenhaForte@123",
            "confirm_password": "SenhaForte@123"
        }
        
        try:
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 201)
        except Exception as e:
            print("Erro no teste de registro de usuário!")
            print("Status Code:", response.status_code if 'response' in locals() else "N/A")
            print("Response Data:", response.data if 'response' in locals() else "N/A")
            print("Exceção:", str(e))
            raise
'''