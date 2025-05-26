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

class TestIntegrationDelete(APITestCase):
    
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
            # Criar uma integração para deletar
            integration_payload = {"gateway": gateway, "name": nameIntegration}
            create_response = self.client.post(self.create_url, integration_payload, format="json")
            self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
            self.integration_uid = create_response.data["uid"]
            self.delete_url = reverse("integration-list") + self.integration_uid + "/" 
        except Exception as e:
            self.fail(f"Erro inesperado no setup: {str(e)}")
            
    def test_delete_integration_invalid_uid(self):
        """
        Testa a exclusão de uma integração com um UID inválido.
        """
        delete_url = reverse("integration-list") + "847b4a59-5ca6-4335-bc97-b2a07e1eddc7/" 
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)
        self.assertEqual(
            response.data["detail"],
            "No Integration matches the given query."
        )

    def test_delete_integration(self):
        """
        Testa a exclusão de uma integração.
        """
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(
            response.data["message"],
            "Integração excluída com sucesso."
        )

        # Verifica se a integração foi realmente deletada
        response = self.client.get(self.delete_url) # essa URL simula o detalhes da integração
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
