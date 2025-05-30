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
TEST_EMAIL = "tester@gmail.com"
TEST_CPF = "63861694921"
TEST_NAME = "Sarah Isabela Lima"
TEST_PASSWORD = "7lonAzJxss@"

INTEGRATION_GATEWAY = "zeroone"
INTEGRATION_NAME = "Conta da Sarah - ZeroOne"

CAMPAIGN_TITLE = "Campanha APP da Sara"
CAMPAIGN_DESCRIPTION = "Campanha de teste para o APP da Sara"
CAMPAIGN_METHOD = "CPC"
CAMPAIGN_AMOUNT = 4.25

KWAI_ACCOUNT_NAME = "Conta da Sarah - Kwai"

class KwaiAccountListingTests(APITestCase):
    
    def setUp(self):
        try:
            # URLs principais
            self.register_url = reverse("account-create-list")
            self.login_url = reverse("login")

            # Criação de usuário
            user_payload = {
                "email": TEST_EMAIL,
                "cpf": TEST_CPF,
                "name": TEST_NAME,
                "password": TEST_PASSWORD,
                "confirm_password": TEST_PASSWORD,
            }
            reg_resp = self.client.post(self.register_url, user_payload, format="json")
            self.assertEqual(reg_resp.status_code, status.HTTP_201_CREATED)

            # Adicionar uma assinatura para o usuário
            user = User.objects.get(email=TEST_EMAIL)
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
            
            # Autenticação
            auth_payload = {"identifier": TEST_EMAIL, "password": TEST_PASSWORD}
            auth_resp = self.client.post(self.login_url, auth_payload, format="json")
            self.assertEqual(auth_resp.status_code, status.HTTP_200_OK)
            token = auth_resp.data.get("access")
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

            # Criação de integração para a primeira conta Kwai
            self.integration_url = reverse("integration-list")
            integration_payload_1 = {"gateway": INTEGRATION_GATEWAY, "name": INTEGRATION_NAME}
            int_resp_1 = self.client.post(self.integration_url, integration_payload_1, format="json")
            self.assertEqual(int_resp_1.status_code, status.HTTP_201_CREATED)
            self.integration_uid_1 = int_resp_1.data.get("uid")

            # Criação de campanha para a primeira conta Kwai
            self.campaign_url = reverse("campaign-list")
            campaign_payload_1 = {
                "title": CAMPAIGN_TITLE,
                "description": CAMPAIGN_DESCRIPTION,
                "integrations": [self.integration_uid_1],
                "method": CAMPAIGN_METHOD,
                "CPC": CAMPAIGN_AMOUNT
            }
            camp_resp_1 = self.client.post(self.campaign_url, campaign_payload_1, format="json")
            self.assertEqual(camp_resp_1.status_code, status.HTTP_201_CREATED)
            self.campaign_uid_1 = camp_resp_1.data.get("uid")

            # Criação da primeira conta Kwai
            self.kwai_url = reverse("kwai-list")
            kwai_payload_1 = {"name": KWAI_ACCOUNT_NAME, "campaigns": [{"uid": self.campaign_uid_1}]}
            kwai_resp_1 = self.client.post(self.kwai_url, kwai_payload_1, format="json")
            self.assertEqual(kwai_resp_1.status_code, status.HTTP_201_CREATED)
            self.kwai_uid_1 = kwai_resp_1.data.get("uid")

            # Criação de integração para a segunda conta Kwai
            integration_payload_2 = {"gateway": "wolfpay", "name": "Integração com GhostPay"}
            int_resp_2 = self.client.post(self.integration_url, integration_payload_2, format="json")
            self.assertEqual(int_resp_2.status_code, status.HTTP_201_CREATED)
            self.integration_uid_2 = int_resp_2.data.get("uid")

            # Criação de campanha para a segunda conta Kwai
            campaign_payload_2 = {
                "title": "Outra Campanha",
                "description": "Descrição da outra campanha",
                "integrations": [self.integration_uid_2],
                "method": CAMPAIGN_METHOD,
                "CPC": CAMPAIGN_AMOUNT
            }
            camp_resp_2 = self.client.post(self.campaign_url, campaign_payload_2, format="json")
            self.assertEqual(camp_resp_2.status_code, status.HTTP_201_CREATED)
            self.campaign_uid_2 = camp_resp_2.data.get("uid")

            # Criação da segunda conta Kwai
            kwai_payload_2 = {"name": "Segunda Conta Kwai", "campaigns": [{"uid": self.campaign_uid_2}]}
            kwai_resp_2 = self.client.post(self.kwai_url, kwai_payload_2, format="json")
            self.assertEqual(kwai_resp_2.status_code, status.HTTP_201_CREATED)
            self.kwai_uid_2 = kwai_resp_2.data.get("uid")
            
            self.listing_url = reverse("kwai-list")
            self.preview_url_1 = reverse("kwai-detail", kwargs={"uid": self.kwai_uid_1})
            self.preview_url_2 = reverse("kwai-detail", kwargs={"uid": self.kwai_uid_2})
        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {e}")
        except Exception as e:
            self.fail(f"Erro inesperado no setUp: {e}")
    
    def test_list_order(self):
        """
        Testa a listagem de contas Kwai, verificando a ordem e os dados retornados.
        """
        response = self.client.get(self.listing_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)
        
        kwai_1 = response.data["results"][1]
        self.assertIsNotNone(kwai_1.get("created_at"))
        self.assertIn("uid", kwai_1)
        self.assertEqual(kwai_1["name"], KWAI_ACCOUNT_NAME) 

        # Verifica os dados da segunda campanha
        kwai_2 = response.data["results"][0]
        self.assertIsNotNone(kwai_2.get("created_at"))
        self.assertIn("uid", kwai_2)
        self.assertEqual(kwai_2["name"], "Segunda Conta Kwai")
        
    def test_filter_by_title(self):
        """
        Testa a listagem filtrada pelo título.
        """
        response = self.client.get(f"{self.listing_url}?search={KWAI_ACCOUNT_NAME}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        result = response.data["results"][0]
        self.assertEqual(result["name"], KWAI_ACCOUNT_NAME)
        self.assertIsNotNone(result.get("created_at"))
        self.assertEqual(result["uid"], str(self.kwai_uid_1))
        self.assertEqual(str(result["campaigns"][0]['uid']), str(self.campaign_uid_1))
        
    def test_invalid_filter(self):
        """
        Testa a listagem com um filtro inválido.
        """
        response = self.client.get(f"{self.listing_url}?search=ABCDEFGHIJKL")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["results"]), 0)
        
    def test_filter_with_html_injection_title(self):
        """
        Testa a listagem com injeção de HTML no filtro de nome.
        """
        html_payload = "<script>alert('XSS')</script>"
        response = self.client.get(f"{self.listing_url}?search={html_payload}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["detail"], 'O parâmetro de busca contém caracteres inválidos.')
        
        
        