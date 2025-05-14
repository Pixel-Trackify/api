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

gateway = "zeroone"
nameIntegration = "Conta da Sarah - ZeroOne"

namecampaign = "Campanha APP da Sara"
descriptionCampaign = "Campanha de teste para o APP da Sara"
methodCampaign = "CPC"
amountCampaign = 4.25

"""
@todo: adicionar validações de retorno, simulando requisiões de view/click do Kwai e Integrações (Receitas)
"""
class TestCampaignDetail(APITestCase):
    
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
            
            self.preview_url = reverse("campaign-detail", kwargs={"uid": self.campaign_uid})
            
        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {str(e)}")
            print(f"Rota não encontrada: {str(e)}")
        except Exception as e:
            self.fail(f"Erro inesperado: {str(e)}")
            print(f"Erro inesperado: {str(e)}")
          
    def test_get_campaign_detail(self):
        """
        Testa a obtenção dos detalhes de uma campanha.
        """
        response = self.client.get(self.preview_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        expected_keys = [
            "uid",
            "integrations",
            "user",
            "title",
            "source",
            "description",
            "CPM",
            "CPV",
            "method",
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
        self.assertEqual(response.data["title"],namecampaign) 
        self.assertEqual(response.data["description"], descriptionCampaign)
        self.assertEqual(response.data["method"], methodCampaign)
        self.assertEqual(str(response.data["uid"]), str(self.campaign_uid))
        self.assertEqual(str(response.data["integrations"][0]), str(self.uid_integration))
        self.assertEqual(response.data["CPC"], str(amountCampaign))
        self.assertEqual(response.data["stats"], {"CREDIT_CARD": 0, "DEBIT_CARD": 0, "PIX": 0, "BOLETO": 0})
        
    def test_get_campaign_detail_not_found(self):
        """
        Testa a obtenção dos detalhes de uma campanha que não existe.
        """
        invalid_uid = str(UUID(int=0))
        detail_url = self.create_url + invalid_uid + "/"
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)
        self.assertEqual(
            response.data["detail"],
            "No Campaign matches the given query."
        ) 
