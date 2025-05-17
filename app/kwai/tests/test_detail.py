from django.contrib.auth import get_user_model
from django.urls import reverse, NoReverseMatch
from rest_framework import status
from rest_framework.test import APITestCase
from uuid import UUID

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

class KwaiAccountDetailTests(APITestCase):
    
    """
    Testes de integração para endpoints de criação e validação de contas Kwai.
    """
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

            # Autenticação
            auth_payload = {"identifier": TEST_EMAIL, "password": TEST_PASSWORD}
            auth_resp = self.client.post(self.login_url, auth_payload, format="json")
            self.assertEqual(auth_resp.status_code, status.HTTP_200_OK)
            token = auth_resp.data.get("access")
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

            # Criação de integração
            self.integration_url = reverse("integration-list")
            integration_payload = {"gateway": INTEGRATION_GATEWAY, "name": INTEGRATION_NAME}
            int_resp = self.client.post(self.integration_url, integration_payload, format="json")
            self.assertEqual(int_resp.status_code, status.HTTP_201_CREATED)
            self.integration_uid = int_resp.data.get("uid")

            # Criação de campanha
            self.campaign_url = reverse("campaign-list")
            campaign_payload = {
                "title": CAMPAIGN_TITLE,
                "description": CAMPAIGN_DESCRIPTION,
                "integrations": [self.integration_uid],
                "method": CAMPAIGN_METHOD,
                "CPC": CAMPAIGN_AMOUNT
            }
            camp_resp = self.client.post(self.campaign_url, campaign_payload, format="json")
            self.assertEqual(camp_resp.status_code, status.HTTP_201_CREATED)
            self.campaign_uid = camp_resp.data.get("uid")     
                   
            # Criação de conta Kwai para visualizar os details
            self.kwai_url = reverse("kwai-list")
            kwai_payload = {"name": KWAI_ACCOUNT_NAME, "campaigns": [{"uid": self.campaign_uid}]}
            kwai_resp = self.client.post(self.kwai_url, kwai_payload, format="json")
            self.assertEqual(kwai_resp.status_code, status.HTTP_201_CREATED)
            self.kwai_uid = kwai_resp.data.get("uid")
            
            self.preview_url = reverse("kwai-detail", kwargs={"uid": self.kwai_uid})
        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {e}")
        except Exception as e:
            self.fail(f"Erro inesperado no setUp: {e}")
        
    def test_get_kwai_detail_not_found(self):
        """
        Testa a obtenção dos detalhes de uma campanha que não existe.
        """
        invalid_uid = str(UUID(int=0))
        detail_url = reverse("kwai-detail", kwargs={"uid": invalid_uid})  
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)
        self.assertEqual(
            response.data["error"],
            "Conta Kwai não encontrada."
        ) 

    def test_get_campaign_detail(self):
        """
        Testa a obtenção dos detalhes de uma campanha.
        """
        response = self.client.get(self.preview_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        expected_keys = [
            "uid",
            "name",
            "user",
            "campaigns",
             "total_approved",
            "total_pending",
            "amount_approved",
            "amount_pending",
            "total_abandoned",
            "amount_abandoned",
            "total_canceled",
            "amount_canceled",
            "total_refunded",
            "amount_refunded",
            "total_rejected",
            "amount_rejected",
            "total_chargeback",
            "amount_chargeback",
            "total_ads",
            "profit",
            "ROI",
            "total_views",
            "total_clicks",
            "stats",
            "overviews"
        ]
        
        # verificar quase todas as colunas usadas nos gráficos
        for key in expected_keys:
            self.assertIn(key, response.data)
        
        # verificar outras colunas que podem ser recuperadas após o cadastro da campanha no setup
        self.assertEqual(response.data["name"], KWAI_ACCOUNT_NAME) 
        self.assertEqual(str(response.data["uid"]), str(self.kwai_uid))
        self.assertEqual(str(response.data["campaigns"][0]["uid"]),  str(self.campaign_uid))
        self.assertEqual(str(response.data["campaigns"][0]["title"]),  str(CAMPAIGN_TITLE))
        self.assertEqual(response.data["campaigns"][0]["in_use"],  True)
        
        self.assertEqual(response.data["stats"]["CARD_CREDIT"], 0) # deveria ser CREDIT_CARD
        self.assertEqual(response.data["stats"]["DEBIT_CARD"], 0)
        self.assertEqual(response.data["stats"]["PIX"], 0)
        self.assertEqual(response.data["stats"]["BOLETO"], 0)
        
    def test_get_kwai_detail_other_user(self):
        """
        Testa se um usuário não pode acessar os detalhes de uma conta Kwai de outro usuário.
        """
        # Criação de um novo usuário
        other_user_payload = {
            "email": "otheruser@gmail.com",
            "cpf": "52641983303",
            "name": "Outro Usuário",
            "password": TEST_PASSWORD,
            "confirm_password": TEST_PASSWORD,
        }
        reg_resp = self.client.post(self.register_url, other_user_payload, format="json")
        self.assertEqual(reg_resp.status_code, status.HTTP_201_CREATED)

        # Autenticação do novo usuário
        auth_payload = {"identifier": "otheruser@gmail.com", "password": TEST_PASSWORD}
        auth_resp = self.client.post(self.login_url, auth_payload, format="json")
        self.assertEqual(auth_resp.status_code, status.HTTP_200_OK)
        token = auth_resp.data.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Tentativa de acessar os detalhes da conta Kwai do primeiro usuário
        response = self.client.get(self.preview_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)
        self.assertEqual(
            response.data["error"],
            "Conta Kwai não encontrada."
        )

