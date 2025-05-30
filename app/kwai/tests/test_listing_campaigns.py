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

CAMPAIGN_TITLE3 = "Motorola G31"
CAMPAIGN_TITLE2 =  "Venda Guaraná"
CAMPAIGN_TITLE = "Campanha APP da Sara"
CAMPAIGN_DESCRIPTION = "Campanha de teste para o APP da Sara"
CAMPAIGN_METHOD = "CPC"
CAMPAIGN_AMOUNT = 4.25

KWAI_ACCOUNT_NAME = "Conta da Sarah - Kwai"

"""
Testes para o endpoint que lista as campanhas disponíveis para a conta Kwai
"""
class KwaiCampaignsTests(APITestCase):
    
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

            # Criação de integrações (3 diferentes)
            self.integration_url = reverse("integration-list")
            integration_payload_1 = {"gateway": INTEGRATION_GATEWAY, "name": INTEGRATION_NAME}
            int_resp_1 = self.client.post(self.integration_url, integration_payload_1, format="json")
            self.assertEqual(int_resp_1.status_code, status.HTTP_201_CREATED)
            integration_uid_1 = int_resp_1.data.get("uid")

            integration_payload_2 = {"gateway": INTEGRATION_GATEWAY, "name": INTEGRATION_NAME + " 2"}
            int_resp_2 = self.client.post(self.integration_url, integration_payload_2, format="json")
            self.assertEqual(int_resp_2.status_code, status.HTTP_201_CREATED)
            integration_uid_2 = int_resp_2.data.get("uid")

            integration_payload_3 = {"gateway": INTEGRATION_GATEWAY, "name": INTEGRATION_NAME + " 3"}
            int_resp_3 = self.client.post(self.integration_url, integration_payload_3, format="json")
            self.assertEqual(int_resp_3.status_code, status.HTTP_201_CREATED)
            integration_uid_3 = int_resp_3.data.get("uid")

            # Criação de campanhas (cada uma com uma integração diferente)
            self.campaign_url = reverse("campaign-list")
            campaign_payload_1 = {
                "title": CAMPAIGN_TITLE,
                "description": CAMPAIGN_DESCRIPTION,
                "integrations": [integration_uid_1],
                "method": CAMPAIGN_METHOD,
                "CPC": CAMPAIGN_AMOUNT
            }
            camp_resp_1 = self.client.post(self.campaign_url, campaign_payload_1, format="json")
            self.assertEqual(camp_resp_1.status_code, status.HTTP_201_CREATED)
            self.campaign_uid_1 = camp_resp_1.data.get("uid")

            campaign_payload_2 = {
                "title": CAMPAIGN_TITLE2,
                "description": CAMPAIGN_DESCRIPTION + " 2",
                "integrations": [integration_uid_2],
                "method": CAMPAIGN_METHOD,
                "CPC": CAMPAIGN_AMOUNT
            }
            camp_resp_2 = self.client.post(self.campaign_url, campaign_payload_2, format="json")
            self.assertEqual(camp_resp_2.status_code, status.HTTP_201_CREATED)
            self.campaign_uid_2 = camp_resp_2.data.get("uid")

            campaign_payload_3 = {
                "title": CAMPAIGN_TITLE3,
                "description": CAMPAIGN_DESCRIPTION + " 3",
                "integrations": [integration_uid_3],
                "method": CAMPAIGN_METHOD,
                "CPC": CAMPAIGN_AMOUNT
            }
            camp_resp_3 = self.client.post(self.campaign_url, campaign_payload_3, format="json")
            self.assertEqual(camp_resp_3.status_code, status.HTTP_201_CREATED)
            self.campaign_uid_3 = camp_resp_3.data.get("uid")
            self.kwai_url = reverse("kwai-list")
            # Criação de conta Kwai com as duas campanhas
            """ 
            kwai_payload = {
                "name": KWAI_ACCOUNT_NAME,
                "campaigns": [{"uid": campaign_uid_1}, {"uid": campaign_uid_2}]
            }
            kwai_resp = self.client.post(self.kwai_url, kwai_payload, format="json")
            self.assertEqual(kwai_resp.status_code, status.HTTP_201_CREATED)
            self.kwai_uid = kwai_resp.data.get("uid")
            self.kwai_update_url = f"{self.kwai_url}{self.kwai_uid}/"""

        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {e}")
        except Exception as e:
            self.fail(f"Erro inesperado no setUp: {e}")
            
    def test_list_campaigns(self):
        """Testa se a listagem de campanhas retorna os dados e ordem corretos."""
        try:
            url = reverse("campaigns_not_in_use")
            resp = self.client.get(url, format="json")
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            expected = [
                (self.campaign_uid_3, CAMPAIGN_TITLE3),
                (self.campaign_uid_2, CAMPAIGN_TITLE2),
                (self.campaign_uid_1, CAMPAIGN_TITLE),
            ]
            for i, (uid, title) in enumerate(expected):
                self.assertEqual(resp.data[i]["uid"], uid)
                self.assertEqual(resp.data[i]["title"], title)
                self.assertFalse(resp.data[i]["in_use"])
        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {e}")
        except Exception as e:
            self.fail(f"Erro inesperado no teste: {e}")      

    def test_list_campaigns_with_kwai_check_is_used(self):
        """Testa se a listagem de campanhas retorna os dados e ordem corretos quando uma campanha está em uso."""
        kwai_payload = {
            "name": KWAI_ACCOUNT_NAME,
            "campaigns": [{"uid": self.campaign_uid_2}, {"uid": self.campaign_uid_3}]
        }
        kwai_resp = self.client.post(self.kwai_url, kwai_payload, format="json")
        self.assertEqual(kwai_resp.status_code, status.HTTP_201_CREATED)
        self.kwai_uid = kwai_resp.data.get("uid")
        
        url = reverse("campaigns_not_in_use")
        resp = self.client.get(url, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        
        self.assertEqual(resp.data[0]["uid"], self.campaign_uid_1)
        self.assertEqual(resp.data[0]["title"], CAMPAIGN_TITLE)
        self.assertFalse(resp.data[0]["in_use"])
        
    def test_list_campaigns_with_kwai_check_is_used_when_deleted(self):    
        """Testa se a listagem de campanhas retorna os dados e ordem corretos quando uma campanha está em uso e é deletada."""
        kwai_payload = {
            "name": KWAI_ACCOUNT_NAME,
            "campaigns": [{"uid": self.campaign_uid_1}, {"uid": self.campaign_uid_2}, {"uid": self.campaign_uid_3}]
        }
        kwai_resp = self.client.post(self.kwai_url, kwai_payload, format="json")
        self.assertEqual(kwai_resp.status_code, status.HTTP_201_CREATED)
        kwai_uid = kwai_resp.data.get("uid")
        
        # Deletar campanha
        delete_url = reverse("kwai-detail", kwargs={"uid": kwai_uid})
        delete_resp = self.client.delete(delete_url, format="json")
        self.assertEqual(delete_resp.status_code, status.HTTP_200_OK)
         
        # Verificar se as campanhas agora estão disponíveis
        url = reverse("campaigns_not_in_use")
        resp = self.client.get(url, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        expected = [
            (self.campaign_uid_3, CAMPAIGN_TITLE3),
            (self.campaign_uid_2, CAMPAIGN_TITLE2),
            (self.campaign_uid_1, CAMPAIGN_TITLE),
        ]
        for i, (uid, title) in enumerate(expected):
            self.assertEqual(resp.data[i]["uid"], uid)
            self.assertEqual(resp.data[i]["title"], title)
            self.assertFalse(resp.data[i]["in_use"])
            
    def test_list_campaigns_with_kwai_check_is_used_when_deleted_bulk(self):    
        """Testa se a listagem de campanhas retorna os dados e ordem corretos quando uma campanha está em uso e é deletada."""
        kwai_payload = {
            "name": KWAI_ACCOUNT_NAME,
            "campaigns": [{"uid": self.campaign_uid_1}, {"uid": self.campaign_uid_2}, {"uid": self.campaign_uid_3}]
        }
        kwai_resp = self.client.post(self.kwai_url, kwai_payload, format="json")
        self.assertEqual(kwai_resp.status_code, status.HTTP_201_CREATED)
        kwai_uid = kwai_resp.data.get("uid")
        
        # Deletar campanha
        delete_url = reverse("kwai-delete-multiple")
        payload = {
            "uids": [kwai_uid]
        }
        delete_resp = self.client.post(delete_url, payload, format="json")
        self.assertEqual(delete_resp.status_code, status.HTTP_200_OK)
         
        # Verificar se as campanhas agora estão disponíveis
        url = reverse("campaigns_not_in_use")
        resp = self.client.get(url, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        expected = [
            (self.campaign_uid_3, CAMPAIGN_TITLE3),
            (self.campaign_uid_2, CAMPAIGN_TITLE2),
            (self.campaign_uid_1, CAMPAIGN_TITLE),
        ]
        for i, (uid, title) in enumerate(expected):
            self.assertEqual(resp.data[i]["uid"], uid)
            self.assertEqual(resp.data[i]["title"], title)
            self.assertFalse(resp.data[i]["in_use"])
            
    def test_list_campaigns_with_kwai_check_is_used_when_update(self):
        """Testa se a listagem de campanhas retorna os dados e ordem corretos quando uma campanha está em uso."""
        kwai_payload = {
            "name": KWAI_ACCOUNT_NAME,
            "campaigns": [{"uid": self.campaign_uid_1}, {"uid": self.campaign_uid_2}, {"uid": self.campaign_uid_3}]
        }
        kwai_resp = self.client.post(self.kwai_url, kwai_payload, format="json")
        self.assertEqual(kwai_resp.status_code, status.HTTP_201_CREATED)
        kwai_uid = kwai_resp.data.get("uid")
    
        # Atualizar campanha
        kwai_update_url = f"{self.kwai_url}{kwai_uid}/"
        kwai_payload_update = {
            "name": KWAI_ACCOUNT_NAME,
            "campaigns": [{"uid": self.campaign_uid_2}, {"uid": self.campaign_uid_3}]
        }
        resp_update = self.client.put(kwai_update_url, kwai_payload_update, format="json")
        self.assertEqual(resp_update.status_code, status.HTTP_200_OK)
        
        # Verificar se a campanha 1 agora está disponível
        url = reverse("campaigns_not_in_use")
        resp = self.client.get(url, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        
        self.assertEqual(resp.data[0]["uid"], self.campaign_uid_1)
        self.assertEqual(resp.data[0]["title"], CAMPAIGN_TITLE)
        self.assertFalse(resp.data[0]["in_use"])
            
