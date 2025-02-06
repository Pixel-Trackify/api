from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import Usuario  
from .models import Plan


class PlanTests(APITestCase):
    def create_user(self, email, cpf, password, is_admin=False):
        """Função auxiliar para criar usuários de forma reutilizável."""
        user_data = {
            "email": email,
            "cpf": cpf,
            "password": password,
            "name": "Usuário Teste" if not is_admin else "Administrador",
        }
        user = Usuario.objects.create_user(**user_data)
        if is_admin:
            user.is_superuser = True
            user.is_staff = True
            user.save()
        return user

    def authenticate_user(self, email, password):
        """Autentica o usuário e armazena o token."""
        login_url = reverse("login")
        login_data = {"identifier": email, "password": password}
        response = self.client.post(login_url, login_data, format="json")

        if response.status_code != status.HTTP_200_OK or "access" not in response.data:
            self.fail(f"Falha ao autenticar usuário: {response.data}")

        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return token

    def setUp(self):
        """Criação de usuários e autenticação do admin."""
        self.user = self.create_user(
            "test@example.com", "97359116040", "Senha@123")
        self.admin_user = self.create_user(
            "admin@example.com", "57885953041", "Admin@123", is_admin=True)
        self.admin_token = self.authenticate_user(
            "admin@example.com", "Admin@123")
        self.plan = Plan.objects.create(
            name='Basic Plan', description='Basic plan description', price=10.0)

    def test_list_plans(self):
        """Teste para listar todos os planos."""
        url = reverse('plan-list')
        response = self.client.get(url)
        # Debug: imprimir dados da resposta
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         f"Erro ao listar planos: {response.data}")

    def test_create_plan(self):
        """Teste para criar um novo plano (somente administrador)."""
        # Autenticar como administrador
        self.client.logout()
        self.authenticate_user("admin@example.com", "Admin@123")

        url = reverse('plan-list')
        data = {'name': 'Premium Plan',
                'description': 'Premium plan description', 'price': 20.0}
        response = self.client.post(url, data, format='json')
        # Debug: imprimir dados da resposta
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                         f"Erro ao criar plano: {response.data}")

    def test_create_plan_non_admin(self):
        """Teste para garantir que um usuário comum não possa criar um plano."""
        # Autenticar como usuário comum
        self.client.logout()
        self.authenticate_user("test@example.com", "Senha@123")

        url = reverse('plan-list')
        data = {'name': 'Premium Plan',
                'description': 'Premium plan description', 'price': 20.0}
        response = self.client.post(url, data, format='json')
        # Debug: imprimir dados da resposta
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         f"Usuário comum conseguiu criar plano: {response.data}")

    def test_retrieve_plan(self):
        """Teste para detalhar um plano específico."""
        url = reverse('plan-detail', args=[self.plan.id])
        response = self.client.get(url)
        # Debug: imprimir dados da resposta
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         f"Erro ao detalhar plano: {response.data}")

    def test_update_plan(self):
        """Teste para atualizar um plano específico (somente administrador)."""
        # Autenticar como administrador
        self.client.logout()
        self.authenticate_user("admin@example.com", "Admin@123")

        url = reverse('plan-detail', args=[self.plan.id])
        data = {'name': 'Updated Plan',
                'description': 'Updated plan description', 'price': 15.0}
        response = self.client.put(url, data, format='json')
        # Debug: imprimir dados da resposta
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         f"Erro ao atualizar plano: {response.data}")

    def test_partial_update_plan(self):
        """Teste para atualizar parcialmente um plano específico (somente administrador)."""
        # Autenticar como administrador
        self.client.logout()
        self.authenticate_user("admin@example.com", "Admin@123")

        url = reverse('plan-detail', args=[self.plan.id])
        data = {'price': 12.0}
        response = self.client.patch(url, data, format='json')
        # Debug: imprimir dados da resposta
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         f"Erro ao atualizar parcialmente plano: {response.data}")

    def test_delete_plan(self):
        """Teste para excluir um plano específico (somente administrador)."""
        # Autenticar como administrador
        self.client.logout()
        self.authenticate_user("admin@example.com", "Admin@123")

        url = reverse('plan-detail', args=[self.plan.id])
        response = self.client.delete(url)
        # Debug: imprimir código de status da resposta
        print(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                         f"Erro ao excluir plano: {response.data}")

    def test_create_subscription(self):
        """Teste para criar uma nova assinatura de usuário."""
        self.client.logout()
        self.authenticate_user("test@example.com", "Senha@123")
        url = reverse('subscription-create')
        data = {
            'plan': self.plan.id,
            'end_date': '2023-12-31'  # Adicionar o campo end_date
        }
        response = self.client.post(url, data, format='json')
        # Debug: imprimir dados da resposta
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                         f"Erro ao criar assinatura: {response.data}")
