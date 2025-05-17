from django.contrib.auth import get_user_model
from django.urls import reverse, NoReverseMatch
from rest_framework import status
from rest_framework.test import APITestCase
from uuid import UUID

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
@todo: verificar listagem de campanhas de outro usuário
@todo: verificar paginação ( cadastrar 11 campanhas )
"""
class TestCampaignListing(APITestCase):
    
    def setUp(self):
        try:
            self.register_url = reverse("account-create-list")
            self.login_url = reverse("login")
            # Criar usuário
            payload = {"email": email, "cpf": cpf, "name": name,
                       "password": password, "confirm_password": password}
            reg_response = self.client.post(self.register_url, payload, format="json")
            self.assertEqual(reg_response.status_code, status.HTTP_201_CREATED)

            # Autenticar para obter token
            login_payload = {"identifier": email, "password": password}
            login_response = self.client.post(self.login_url, login_payload, format="json")
            self.assertEqual(login_response.status_code, status.HTTP_200_OK)
            self.access_token = login_response.data.get("access")
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

            # Criar integração
            integration_payload = {"gateway": gateway, "name": nameIntegration}
            integration_response = self.client.post(reverse("integration-list"), integration_payload, format="json")
            self.assertEqual(integration_response.status_code, status.HTTP_201_CREATED)
            self.uid_integration = integration_response.data.get("uid")

            # Criar primeira campanha
            self.create_url = reverse("campaign-list")
            campaign_payload_1 = {
                "title": namecampaign,
                "description": descriptionCampaign,
                "integrations": [self.uid_integration],
                "method": methodCampaign,
                "CPC": amountCampaign
            }
            response_1 = self.client.post(self.create_url, campaign_payload_1, format="json")
            self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)

            # Criar integração antes de criar a segunda campanha
            integration_payload = {"gateway": "tribopay", "name": "Conta da Zoey - TriboPay"}
            integration_response = self.client.post(reverse("integration-list"), integration_payload, format="json")
            self.assertEqual(integration_response.status_code, status.HTTP_201_CREATED)
            self.uid_integration2 = integration_response.data.get("uid")
            
            # Criar segunda campanha
            campaign_payload_2 = {
                "title": "Segunda Campanha",
                "description": "Descrição da segunda campanha",
                "integrations": [self.uid_integration2],
                "method": "CPV",
                "CPV": 5.50
            }
            response_2 = self.client.post(self.create_url, campaign_payload_2, format="json")
            self.assertEqual(response_2.status_code, status.HTTP_201_CREATED)

        except Exception as e:
            self.fail(f"Erro inesperado no setup: {str(e)}")

    def test_list_campaigns(self):
        """
        Testa a listagem de campanhas.
        """
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)

        # Verifica os dados da primeira campanha
        campaign_1 = response.data["results"][1]
        self.assertIn("uid", campaign_1)
        self.assertEqual(campaign_1["title"], namecampaign)
        self.assertEqual(campaign_1["description"], descriptionCampaign)
        self.assertEqual(campaign_1["method"], methodCampaign)
        self.assertEqual(campaign_1["CPC"], str(amountCampaign))

        # Verifica os dados da segunda campanha
        campaign_2 = response.data["results"][0]
        self.assertIn("uid", campaign_2)
        self.assertEqual(campaign_2["title"], "Segunda Campanha")
        self.assertEqual(campaign_2["description"], "Descrição da segunda campanha")
        self.assertEqual(campaign_2["method"], "CPV")
        self.assertEqual(campaign_2["CPV"], "5.50")
        
    def test_filter_by_title(self):
        """
        Testa a listagem filtrada pelo título.
        """
        response = self.client.get(f"{self.create_url}?search={namecampaign}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        result = response.data["results"][0]
        self.assertEqual(result["title"], namecampaign)
        self.assertEqual(result["description"], descriptionCampaign)
        self.assertEqual(result["method"], methodCampaign)
        self.assertEqual(result["CPC"], str(amountCampaign))
        self.assertEqual(result["uid"], str(result["uid"]))
        self.assertEqual(str(result["integrations"][0]), str(self.uid_integration))
    
    def test_filter_by_description(self):
        """
        Testa a listagem filtrada pela descrição.
        """
        response = self.client.get(f"{self.create_url}?search=Descrição da segunda campanha")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        result = response.data["results"][0]
        self.assertEqual(result["title"], "Segunda Campanha")
        self.assertEqual(result["description"], "Descrição da segunda campanha")
        self.assertEqual(result["method"], "CPV")
        self.assertEqual(result["CPV"], "5.50")
        self.assertEqual(result["uid"], str(result["uid"]))
        self.assertEqual(str(result["integrations"][0]), str(self.uid_integration2))

    def test_filter_by_method(self):
        """
        Testa a listagem filtrada pelo método.
        """
        response = self.client.get(f"{self.create_url}?search=CPC")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        result = response.data["results"][0]
        self.assertEqual(result["title"], namecampaign)
        self.assertEqual(result["description"], descriptionCampaign)
        self.assertEqual(result["method"], methodCampaign)
        self.assertEqual(result["CPC"], str(amountCampaign))
        self.assertEqual(result["uid"], str(result["uid"]))
        self.assertEqual(str(result["integrations"][0]), str(self.uid_integration))
        
    def test_invalid_filter(self):
        """
        Testa a listagem com um filtro inválido.
        """
        response = self.client.get(f"{self.create_url}?search=ABCDEFGHIJKL")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["results"]), 0)
    
    def test_filter_with_html_injection_title(self):
        """
        Testa a listagem com injeção de HTML no filtro de título.
        """
        html_payload = "<script>alert('XSS')</script>"
        response = self.client.get(f"{self.create_url}?search={html_payload}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["detail"], 'O parâmetro de busca contém caracteres inválidos.')