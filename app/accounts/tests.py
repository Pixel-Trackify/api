from django.contrib.auth import get_user_model
from django.urls import reverse, NoReverseMatch
from rest_framework import status
from rest_framework.test import APITestCase
from uuid import UUID
import os

User = get_user_model()

# Dados de exemplo para criação de usuário
email = "tester@gmail.com"
cpf = "63861694921"
name = "Sarah Isabela Lima"
password = "7lonAzJxss@"

"""
@todo:
- Testar validação de campo 'name' aceitar apenas caracteres alfanuméricos e alguns especiais
- Testar bloqueio de conta após N tentativas de login falhas
- Testar limites de tamanho de 'name' (mínimo/máximo)
- Testar se o campo 'avatar' é atualizado corretamente
"""
class TestAccountRegistration(APITestCase):
    """Testes para o endpoint de registro de nova conta."""

    def setUp(self):
        try:
            self.url = reverse("account-create-list")
        except NoReverseMatch:
            self.fail("Rota 'account-create-list' não encontrada em urls.py.")
    def test_registration_fails_with_missing_required_fields(self):
        """Deve retornar 400 quando campos obrigatórios estiverem ausentes."""
        payload = {}  # Nenhum campo enviado
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ['email', 'cpf', 'name', 'password', 'confirm_password']:
            self.assertIn(field, response.data)
            self.assertTrue(
                len(response.data[field]) >= 1, f"Este campo é obrigatório.")

    def test_registration_fails_with_invalid_cpf(self):
        """Deve retornar 400 quando CPF for inválido."""
        payload = {"email": email, "cpf": "12345678901", "name": name,
                   "password": password, "confirm_password": password}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cpf", response.data)
        self.assertEqual(response.data["cpf"], ["CPF inválido."])

    def test_registration_fails_when_passwords_mismatch(self):
        """Deve retornar 400 quando 'password' e 'confirm_password' não coincidirem."""
        payload = {"email": email, "cpf": cpf, "name": name,
                   "password": "abc12345", "confirm_password": "abc54321"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(response.data["password"], [
                         "As senhas não coincidem."])

    def test_registration_fails_with_short_password(self):
        """Deve retornar 400 quando senha tiver menos de 8 caracteres."""
        payload = {"email": email, "cpf": cpf, "name": name,
                   "password": "1234567", "confirm_password": "1234567"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(response.data["password"], [
                         "A senha deve ter no mínimo 8 caracteres."])

    def test_registration_fails_with_long_password(self):
        """Deve retornar 400 quando senha exceder 30 caracteres."""
        long_pwd = "A" * 31
        payload = {"email": email, "cpf": cpf, "name": name,
                   "password": long_pwd, "confirm_password": long_pwd}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(response.data["password"], [
                         "A senha deve ter no máximo 30 caracteres."])

    def test_registration_fails_without_uppercase(self):
        """Deve retornar 400 quando não houver letra maiúscula na senha."""
        payload = {"email": email, "cpf": cpf, "name": name,
                   "password": "abc12345@", "confirm_password": "abc12345@"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(response.data["password"], [
                         "A senha deve conter pelo menos 1 letra maiúscula."])

    def test_registration_fails_without_special_character(self):
        """Deve retornar 400 quando não houver caractere especial na senha."""
        payload = {"email": email, "cpf": cpf, "name": name,
                   "password": "Abc123456", "confirm_password": "Abc123456"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(response.data["password"], [
                         "A senha deve conter pelo menos 1 caractere especial."])

    def test_registration_fails_with_invalid_email_format(self):
        """Deve retornar 400 quando o e-mail tiver formatação inválida."""
        payload = {"email": "bruno@", "cpf": cpf, "name": name,
                   "password": password, "confirm_password": password}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"], [
                         "Insira um endereço de email válido."])

    def test_registration_succeeds_with_valid_data(self):
        """Deve retornar 201 quando todos os dados do registro forem válidos."""
        payload = {"email": email, "cpf": cpf, "name": name,
                   "password": password, "confirm_password": password}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.data

        # Verifica chaves principais
        expected_keys = {'message', 'user',
                         'require_email_confirmation', 'refresh', 'access'}
        self.assertTrue(expected_keys.issubset(data.keys()),
                        "Resposta não contém todas as chaves esperadas.")

        self.assertEqual(data['message'], "Usuário registrado com sucesso!")

        user_block = data['user']
        uid = user_block.get('uid')
        self.assertTrue(isinstance(uid, (str, UUID)),
                        f"UID deve ser str ou UUID, mas é {type(uid)}")
        self.assertEqual(user_block.get('name'), name)
        self.assertEqual(user_block.get('email'), email)
        self.assertIsNone(user_block.get('avatar'))

        # flags e tokens
        self.assertIs(data['require_email_confirmation'], os.getenv("REQUIRE_EMAIL_CONFIRMATION", "True") == "False")
        self.assertIsInstance(data['refresh'], str)
        self.assertTrue(len(data['refresh']) > 0)
        self.assertIsInstance(data['access'], str)
        self.assertTrue(len(data['access']) > 0)

    def test_registration_fails_with_existing_email(self):
        """Deve retornar 400 quando o e-mail já estiver em uso."""
        # Registra o primeiro usuário
        payload = {"email": email, "cpf": cpf, "name": name,
                   "password": password, "confirm_password": password}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # agora tenta registrar o mesmo e-mail e CPF novamente
        self.url = reverse("account-create-list")
        payload = {"email": email, "cpf": cpf, "name": name,
                   "password": password, "confirm_password": password}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn("cpf", response.data)
        self.assertEqual(response.data["email"], [
                         "usuario com este email já existe."])
        self.assertEqual(response.data["cpf"], [
                         "usuario com este cpf já existe."])


class TestProfileUpdate(APITestCase):
    """Testes para endpoints de atualização de perfil de usuário autenticado."""

    def setUp(self):
        # Registrar e autenticar um usuário válido
        try:
            self.register_url = reverse("account-create-list")
            # ajuste conforme sua rota de login
            self.login_url = reverse("login")
            # Criar usuário
            payload = {"email": email, "cpf": cpf, "name": name,
                       "password": password, "confirm_password": password}
            reg_response = self.client.post(
                self.register_url, payload, format="json")
            self.assertEqual(reg_response.status_code, status.HTTP_201_CREATED)

            # Autenticar para obter token
            login_payload = {"identifier": email, "password": password}
            login_response = self.client.post(
                self.login_url, login_payload, format="json")
            self.assertEqual(login_response.status_code, status.HTTP_200_OK)
            self.access_token = login_response.data.get("access")
            # Definir cabeçalho de autorização
            self.client.credentials(
                HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

            # URL para atualizar perfil (detail)
            self.detail_url = reverse("profile")
        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {str(e)}")
            print(f"Rota não encontrada: {str(e)}")
        except Exception as e:
            self.fail(f"Erro inesperado: {str(e)}")
            print(f"Erro inesperado: {str(e)}")

    def test_update_profile_with_invalid_email_format_returns_400(self):
        """Deve retornar 400 quando o formato de email for inválido."""
        payload = {"email": "inválido@", "name": name, "cpf": cpf}
        response = self.client.put(self.detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(response.data["email"], [
                         "Insira um endereço de email válido."])

    def test_update_profile_with_invalid_cpf_length_returns_400(self):
        """Deve retornar 400 quando o CPF exceder 11 caracteres."""
        payload = {"email": email, "name": name, "cpf": "999999999999"}
        response = self.client.put(self.detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cpf', response.data)
        self.assertEqual(response.data["cpf"], [
                         "Certifique-se de que este campo não tenha mais de 11 caracteres."])

    def test_update_profile_with_invalid_cpf_numbers_returns_400(self):
        """Deve retornar 400 quando o CPF tiver sequência numérica inválida."""
        payload = {"email": email, "name": name, "cpf": "00000000000"}
        response = self.client.put(self.detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cpf', response.data)
        self.assertEqual(response.data["cpf"], ["CPF inválido."])

    def test_update_profile_with_duplicate_email_and_cpf_returns_400(self):
        """Deve retornar 400 quando email e CPF já estiverem em uso por outro usuário."""
        # Registra um usuário aleatório primeiro
        dup_email = "email.duplicado@gmail.com"
        dup_cpf = "12519340134"

        self.url = reverse("account-create-list")
        payload = {"email": dup_email, "cpf": dup_cpf, "name": name,
                   "password": password, "confirm_password": password}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        payload = {"email": dup_email, "name": name, "cpf": dup_cpf}
        response = self.client.put(self.detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('cpf', response.data)
        self.assertEqual(response.data["email"], [
                         "usuario com este email já existe."])
        self.assertEqual(response.data["cpf"], [
                         "usuario com este cpf já existe."])

    def test_successful_profile_update_returns_200_and_updated_fields(self):
        """Deve atualizar perfil com dados válidos e retornar 200 com os valores alterados."""
        try:
            new_name = "Maria Silva"
            new_cpf = "55150852996"
            new_email = "tester2@gmail.com"
            payload = {"name": new_name, "email": new_email, "cpf": new_cpf}
            response = self.client.put(self.detail_url, payload, format="json")

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data.get('name'), new_name)
            self.assertEqual(response.data.get('email'), new_email)
            self.assertEqual(response.data.get('cpf'), new_cpf)

        except Exception as e:
            self.fail(f"Erro inesperado: {str(e)}")
            print(f"Erro inesperado: {str(e)}")
