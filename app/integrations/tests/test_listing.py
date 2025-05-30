from django.contrib.auth import get_user_model
from django.urls import reverse, NoReverseMatch
from rest_framework import status
from rest_framework.test import APITestCase
from uuid import UUID
from datetime import timedelta
from django.utils import timezone
from plans.models import Plan
from payments.models import UserSubscription, SubscriptionPayment
import uuid

User = get_user_model()

# Dados de exemplo para criação de usuário
email = "tester@gmail.com"
cpf = "63861694921"
name = "Sarah Isabela Lima"
password = "7lonAzJxss@"

gateway = "zeroone"
nameIntegration = "Conta da Sarah - ZeroOne"

class TestIntegrationListing(APITestCase):
    
    def setUp(self):
        try:
            self.register_url = reverse("account-create-list")
            self.login_url = reverse("login")
            self.create_url = reverse("integration-list")
            # Criar usuário
            payload = {"email": email, "cpf": cpf, "name": name,
                       "password": password, "confirm_password": password}
            reg_response = self.client.post(self.register_url, payload, format="json")
            self.assertEqual(reg_response.status_code, status.HTTP_201_CREATED)

            # Adicionar uma assinatura para o usuário
            user = User.objects.get(email=email)
            user.subscription_active = True
            user.subscription_expiration = timezone.now() + timedelta(days=30)
            user.save()
            
            # Crie um plano de teste
            plan = Plan.objects.create(
                name="Plano Teste",
                price=49.99,
                duration="month",
                duration_value=1,
                is_current=True,
                campaign_limit=5,
                integration_limit=5,
                kwai_limit=5,
                description="Plano de teste para integração"
            )

            # Crie uma assinatura ativa para o usuário
            subscription = UserSubscription.objects.create(
                user=user,
                plan=plan,
                start_date=timezone.now(),
                expiration=timezone.now() + timedelta(days=30),
                is_active=True,
                status="active"
            )

            # Crie um pagamento para a assinatura
            SubscriptionPayment.objects.create(
                uid=uuid.uuid4(),
                idempotency=f"{user.pk}-{plan.uid}-PIX",
                payment_method="PIX",
                gateway="zeroone",
                price=plan.price,
                status=True,
                subscription=subscription
            )
            
            # Autenticar para obter token
            login_payload = {"identifier": email, "password": password}
            login_response = self.client.post(self.login_url, login_payload, format="json")
            self.assertEqual(login_response.status_code, status.HTTP_200_OK)
            self.access_token = login_response.data.get("access")
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
            # Criar duas integrações para listar
            integration_payload_1 = {"gateway": gateway, "name": name + " - ZeroOne" }
            integration_payload_2 = {"gateway": "disrupty", "name": "Teste"}
            self.client.post(self.create_url, integration_payload_1, format="json")
            self.client.post(self.create_url, integration_payload_2, format="json")
        except Exception as e:
            self.fail(f"Erro inesperado no setup: {str(e)}")

    def test_list_integrations(self):
        """
        Testa a listagem de integrações.
        """
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)

        # Verifica os dados da primeira integração
        integration_1 = response.data["results"][1]
        self.assertIn("uid", integration_1)
        self.assertEqual(integration_1["name"], name + " - ZeroOne")
        self.assertEqual(integration_1["gateway"], gateway)
        self.assertFalse(integration_1["deleted"])
        self.assertEqual(integration_1["status"], "active")
        self.assertTrue(integration_1["webhook_url"].startswith("http"))

        # Verifica os dados da segunda integração
        integration_2 = response.data["results"][0]
        self.assertIn("uid", integration_2)
        self.assertEqual(integration_2["name"], "Teste")
        self.assertEqual(integration_2["gateway"], "disrupty")
        self.assertFalse(integration_2["deleted"])
        self.assertEqual(integration_2["status"], "active")
        self.assertTrue(integration_2["webhook_url"].startswith("http"))
        
    def test_list_integrations_with_search_filter(self):
        """
        Testa a listagem de integrações com o filtro de busca (?search).
        """
        # Filtrar integrações pelo nome "Zero"
        response = self.client.get(f"{self.create_url}?search=Zero")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)

        # Verifica os dados da integração retornada
        integration = response.data["results"][0]
        self.assertIn("uid", integration)
        self.assertEqual(integration["name"], name + " - ZeroOne")
        self.assertEqual(integration["gateway"], gateway)
        self.assertEqual(integration["status"], "active")
        self.assertTrue(integration["webhook_url"].startswith("http"))
