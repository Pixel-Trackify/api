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
@todo:
    - Testar com todos os gateways disponíveis
"""
class TestcampaignRegistration(APITestCase):
    
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
            
        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {str(e)}")
            print(f"Rota não encontrada: {str(e)}")
        except Exception as e:
            self.fail(f"Erro inesperado: {str(e)}")
            print(f"Erro inesperado: {str(e)}")
            
    def test_create_campaign_empty_data(self):
        """
        Testa a criação de uma campanha com dados vazios.
        """
        response = self.client.post(self.create_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data) 
        self.assertIn("method", response.data) 
        
        self.assertEqual(
            response.data["title"][0],
            "Este campo é obrigatório."
        ) 
        self.assertEqual(
            response.data["method"][0],
            "Este campo é obrigatório."
        ) 
        
    def test_create_campaign_empty_CPC(self):
        """
        Testa a criação de uma campanha com CPC vazio.
        """
        payload = {
            "title": namecampaign,
            "description": descriptionCampaign,
            "integrations": [self.uid_integration],
            "method": methodCampaign,
            "CPC": ""
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("CPC", response.data)
        self.assertEqual(
            response.data["CPC"][0],
            "Este campo é obrigatório."
        )
    
    def test_create_campaign_invalid_CPV(self):
        """
        Testa a criação de uma campanha com CPV vazio.
        """
        payload = {
            "title": namecampaign,
            "description": descriptionCampaign,
            "integrations": [self.uid_integration],
            "method": "CPV",
            "CPV": ""
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("CPV", response.data)
        self.assertEqual(
            response.data["CPV"][0],
            "Este campo é obrigatório."
        )
    
    def test_create_campaign_invalid_CPM(self):
        """
        Testa a criação de uma campanha com CPM inválido.
        """
        payload = {
            "title": namecampaign,
            "description": descriptionCampaign,
            "integrations": [self.uid_integration],
            "method": "CPM",
            "CPM": ""
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("CPM", response.data)
        self.assertEqual(
            response.data["CPM"][0],
            "Este campo é obrigatório."
        )
   
    def test_html_injection_campaign_title(self):
        """
        Testa a criação de uma campanha com injeção de código HTML no campo 'title'.
        """
        payload = {
            "title": "<script>alert('XSS')</script>",
            "description": descriptionCampaign,
            "integrations": [self.uid_integration],
            "method": methodCampaign,
            "CPC": amountCampaign
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertEqual(
            response.data["title"][0],
            "O campo não pode conter tags HTML."
        )
    
    def test_xrss_attack_campaign_title(self):
        """
        Testa a criação de uma campanha com ataque XSS no campo 'title'.
        """
        payload = {
            "title": "&lt;script&gt;alert(&#x27;XRSS&#x27;);&lt;/script&gt;",
            "description": descriptionCampaign,
            "integrations": [self.uid_integration],
            "method": methodCampaign,
            "CPC": amountCampaign
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertEqual(
            response.data["title"][0],
            "O campo não pode conter tags HTML."
        )
    
    def test_xrss_attack_campaign_emoji(self):
        """
         Testa a criação de uma campanha com Emoji no campo 'title'.
        """
        payload = {
            "title": "😀",
            "description": descriptionCampaign,
            "integrations": [self.uid_integration],
            "method": methodCampaign,
            "CPC": amountCampaign
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertEqual(
            response.data["title"][0],
            "O campo só pode conter caracteres ASCII."
        )
        
    def test_campaign_title_too_short(self):
        """
        Testa a criação de uma campanha com o título muito curto.
        """
        payload = {
            "title": "A",
            "description": descriptionCampaign,
            "integrations": [self.uid_integration],
            "method": methodCampaign,
            "CPC": amountCampaign
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertEqual(
            response.data["title"][0],
            "O campo deve ter pelo menos 5 caracteres."
        )
    
    def test_campaign_title_too_long(self):
        """
        Testa a criação de uma campanha com o título muito longo.
        """
        payload = {
            "title": "A" * 101,
            "description": descriptionCampaign,
            "integrations": [self.uid_integration],
            "method": methodCampaign,
            "CPC": amountCampaign
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertEqual(
            response.data["title"][0],
            "Certifique-se de que este campo não tenha mais de 100 caracteres."
        )
    
    def test_html_injection_campaign_description(self):
        """
        Testa a criação de uma campanha com injeção de código HTML no campo 'description'.
        """
        payload = {
            "title": namecampaign,
            "description": "<script>alert('XSS')</script>",
            "integrations": [self.uid_integration],
            "method": methodCampaign,
            "CPC": amountCampaign
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)
        self.assertEqual(
            response.data["description"][0],
            "O campo não pode conter tags HTML."
        )
    
    def test_xrss_attack_campaign_description(self):
        """
        Testa a criação de uma campanha com ataque XSS no campo 'title'.
        """
        payload = {
            "title": namecampaign,
            "description": "&lt;script&gt;alert(&#x27;XRSS&#x27;);&lt;/script&gt;",
            "integrations": [self.uid_integration],
            "method": methodCampaign,
            "CPC": amountCampaign
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)
        self.assertEqual(
            response.data["description"][0],
            "O campo não pode conter tags HTML."
        )
    
    def test_xrss_attack_campaign_description_emoji(self):
        """
         Testa a criação de uma campanha com Emoji no campo 'description'.
        """
        payload = {
            "title": namecampaign,
            "description": "😀",
            "integrations": [self.uid_integration],
            "method": methodCampaign,
            "CPC": amountCampaign
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)
        self.assertEqual(
            response.data["description"][0],
            "O campo só pode conter caracteres ASCII."
        )
         
    def test_campaign_description_too_short(self):
        """
        Testa a criação de uma campanha com a descrição muito curta.
        """
        payload = {
            "title": namecampaign,
            "description": "A",
            "integrations": [self.uid_integration],
            "method": methodCampaign,
            "CPC": amountCampaign
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)
        self.assertEqual(
            response.data["description"][0],
            "O campo deve ter pelo menos 5 caracteres."
        )
   
    def test_campaign_description_too_long(self):
        """
        Testa a criação de uma campanha com a descrição muito longa.
        """
        payload = {
            "title": namecampaign,
            "description": "A" * 501,
            "integrations": [self.uid_integration],
            "method": methodCampaign,
            "CPC": amountCampaign
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)
        self.assertEqual(
            response.data["description"][0],
            "O campo não pode exceder 500 caracteres."
        )
   
    def test_campaign_invalid_method(self):
        """
        Testa a criação de uma campanha com um método inválido.
        """
        payload = {
            "title": namecampaign,
            "description": descriptionCampaign,
            "integrations": [self.uid_integration],
            "method": "INVALID_METHOD"
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("method", response.data)
        self.assertEqual(
            response.data["method"][0],
             '"INVALID_METHOD" não é um escolha válido.'
        )
        
    def test_create_campaign(self):
        """
        Testa a criação de uma nova campanha.
        """
        payload = {
            "title": namecampaign,
            "description": descriptionCampaign,
            "integrations": [self.uid_integration],
            "method": methodCampaign,
            "CPC": amountCampaign
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("uid", response.data)
        self.assertIn("title", response.data)
        self.assertIn("description", response.data)
        self.assertIn("CPC", response.data)
        
        self.assertEqual(response.data["title"], namecampaign)
        self.assertEqual(response.data["description"], descriptionCampaign)
        self.assertEqual(response.data["CPC"], str(amountCampaign))
        self.assertTrue(UUID(response.data["uid"], version=4))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
