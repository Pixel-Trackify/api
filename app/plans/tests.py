from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from accounts.serializers import RegisterSerializer
from .models import Plan

User = get_user_model()


class AuthenticationTests(APITestCase):
    def create_user(self, email, cpf, password, is_admin=False):
        """Função auxiliar para criar usuários de forma reutilizável."""
        try:
            user_data = {
                "email": email,
                "cpf": cpf,
                "password": password,
                "confirm_password": password,
                "name": "Usuário Teste" if not is_admin else "Administrador",
            }
            serializer = RegisterSerializer(data=user_data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            if is_admin:
                user.is_superuser = True
                user.is_staff = True
                user.save()
            return user
        except Exception as e:
            self.fail(f"Erro ao criar usuário {email}: {str(e)}")

    def authenticate_user(self, email, password):
        """Autentica um usuário e armazena o token."""
        try:
            login_url = reverse("login")
            login_data = {"identifier": email, "password": password}
            response = self.client.post(login_url, login_data, format="json")

            self.assertIsNotNone(response, "Erro: A resposta é None!")
            self.assertEqual(response.status_code, status.HTTP_200_OK,
                             f"Falha ao autenticar usuário {email}: {response.data}")

            token = response.data.get("access")
            self.assertIsNotNone(token, "Erro: Token de acesso não retornado!")

            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        except Exception as e:
            self.fail(f"Erro ao autenticar usuário {email}: {str(e)}")

    def setUp(self):
        """Criação de usuários e autenticação do admin."""
        self.user = self.create_user(
            "test@example.com", "97359116040", "Senha@123")
        self.admin_user = self.create_user(
            "admin@example.com", "57885953041", "Admin@123", is_admin=True)
        self.authenticate_user("admin@example.com", "Admin@123")

        # Criando um plano para os testes
        self.plan = Plan.objects.create(
            name="Plano Básico",
            price=100.00,
            duration=30
        )

    def test_list_plans(self):
        """Teste para listar todos os planos."""
        try:
            url = reverse('plan-list')
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK,
                             f"Erro ao listar planos: {response.data}")
        except Exception as e:
            self.fail(f"Erro ao listar planos: {str(e)}")

    def test_create_plan(self):
        """Teste para criar um novo plano (somente administrador)."""
        try:
            self.client.logout()
            self.authenticate_user("admin@example.com", "Admin@123")

            url = reverse('plan-list')
            data = {'name': 'Premium Plan',
                    'description': 'Premium plan description', 'price': 20.0}
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                             f"Erro ao criar plano: {response.data}")
        except Exception as e:
            self.fail(f"Erro ao criar plano: {str(e)}")

    def test_create_plan_non_admin(self):
        """Teste para garantir que um usuário comum não possa criar um plano."""
        try:
            self.client.logout()
            self.authenticate_user("test@example.com", "Senha@123")

            url = reverse('plan-list')
            data = {'name': 'Premium Plan',
                    'description': 'Premium plan description', 'price': 20.0}
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                             f"Usuário comum conseguiu criar plano: {response.data}")
        except Exception as e:
            self.fail(
                f"Erro ao testar criação de plano por usuário comum: {str(e)}")

    def test_retrieve_plan(self):
        """Teste para detalhar um plano específico."""
        try:
            url = reverse('plan-detail', args=[self.plan.id])
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK,
                             f"Erro ao detalhar plano: {response.data}")
        except Exception as e:
            self.fail(f"Erro ao detalhar plano: {str(e)}")

    def test_delete_plan(self):
        """Teste para excluir um plano específico (somente administrador)."""
        try:
            self.client.logout()
            self.authenticate_user("admin@example.com", "Admin@123")

            url = reverse('plan-detail', args=[self.plan.id])
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                             f"Erro ao excluir plano: {response.data}")
        except Exception as e:
            self.fail(f"Erro ao excluir plano: {str(e)}")
