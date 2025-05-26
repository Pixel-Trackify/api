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

namecampaign = "Campanha APP da Sara"
descriptionCampaign = "Campanha de teste para o APP da Sara"
methodCampaign = "CPC"
amountCampaign = 4.25


class TestCampaignBulkDeletion(APITestCase):
    def setUp(self):
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
            login_response = self.client.post(
                self.login_url, login_payload, format="json")
            self.assertEqual(login_response.status_code, status.HTTP_200_OK)
            self.access_token = login_response.data.get("access")
            self.uid = login_response.data.get("uid")
            # Definir cabeçalho de autorização
            self.client.credentials(
                HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
            
           
            # Criação de uma nova integração.
            payload = {
                "gateway": gateway,
                "name": nameIntegration
            }
            response = self.client.post(reverse("integration-list"), payload, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertIn("webhook_url", response.data)
            self.assertIn("uid", response.data)
            self.assertIn("name", response.data)
            self.assertIn("gateway", response.data)
            self.assertIn("status", response.data)
            self.assertEqual(response.data["gateway"], gateway)
            self.assertEqual(response.data["name"], nameIntegration)
            self.assertTrue(UUID(response.data["uid"], version=4))
            self.assertTrue(response.data["webhook_url"].startswith("http"))
            self.assertIn(gateway.lower(), response.data["webhook_url"])
            self.assertIn(str(response.data["uid"]), response.data["webhook_url"])
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
            self.uid_integration = response.data.get("uid")
            self.create_url = reverse("campaign-list")
            # Cria uma nova campanha 
            payload = {
                "title": namecampaign,
                "description": descriptionCampaign,
                "integrations": [self.uid_integration],
                "method": methodCampaign,
                "CPC": amountCampaign
            }
            
            response_create = self.client.post(self.create_url, payload, format="json")
            self.assertEqual(response_create.status_code, status.HTTP_201_CREATED)
            self.assertIn("uid", response_create.data)
            self.assertIn("title", response_create.data)
            self.assertIn("description", response_create.data)
            self.assertIn("CPC", response_create.data)
            self.assertEqual(response_create.data["title"], namecampaign)
            self.assertEqual(response_create.data["description"], descriptionCampaign)
            self.assertEqual(response_create.data["CPC"], str(amountCampaign))
            self.assertTrue(UUID(response_create.data["uid"], version=4))
            self.campaign_uid = response_create.data.get("uid")
            
            self.delete_url = reverse("campaign-delete-multiple")
            self.detail_url = reverse("campaign-detail", kwargs={"uid": self.campaign_uid})
            self.payload = {"uids": [self.campaign_uid]}
            
        except Exception as e:
            self.fail(f"Erro inesperado no setup: {str(e)}")
            
    def test_bulk_delete_campaigns_invalid_uid(self):
        """
        Testa a exclusão em massa de campanhas com um UID inválido.
        """
        payload = {
            "uids": ["847b4a59-5ca6-4335-bc97-b2a07e1eddc7"]
        }
        response = self.client.post(self.delete_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)
        self.assertEqual(
            response.data["error"],
            "Nenhuma campanha encontrada."
        )       
         
    def test_bulk_delete_campaigns(self):
        """
        Testa a exclusão em massa de campanhas.
        """
        response = self.client.post(self.delete_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(
            response.data["message"],
            "1 campanha(s) excluída(s) com sucesso."
        )
        
        # Verifica se a campanha foi realmente deletada
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_campaign_from_another_user(self):
        """
        Testa a tentativa de exclusão de uma campanha pertencente a outro usuário.
        """
        # Criar um segundo usuário
        second_user_payload = {
            "email": "seconduser@gmail.com",
            "cpf": "52641983303",
            "name": "João da Silva",
            "password": password,
            "confirm_password": password
        }
        second_user_response = self.client.post(self.register_url, second_user_payload, format="json")
        self.assertEqual(second_user_response.status_code, status.HTTP_201_CREATED)

        # Autenticar o segundo usuário
        second_user_login_payload = {
            "identifier": second_user_payload["email"],
            "password": password
        }
        second_user_login_response = self.client.post(self.login_url, second_user_login_payload, format="json")
        self.assertEqual(second_user_login_response.status_code, status.HTTP_200_OK)
        second_user_access_token = second_user_login_response.data.get("access")

        # Definir o cabeçalho de autorização para o segundo usuário
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {second_user_access_token}")

        # Tentar excluir a campanha do primeiro usuário
        response = self.client.post(self.delete_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)
        self.assertEqual(
            response.data["error"],
            "Nenhuma campanha encontrada."
        )