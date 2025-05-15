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

nameKwai = "Conta da Sarah - Kwai"

class TestKwaiRegistration(APITestCase):
    
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
            self.create_campaign_url = reverse("campaign-list")
            
            # Cria uma nova campanha 
            payload = {
                "title": namecampaign,
                "description": descriptionCampaign,
                "integrations": [self.uid_integration],
                "method": methodCampaign,
                "CPC": amountCampaign
            }
            
            response_create = self.client.post(self.create_campaign_url, payload, format="json")
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
            
            self.create_url = reverse("kwai-list")
        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {str(e)}")
            print(f"Rota não encontrada: {str(e)}")
        except Exception as e:
            self.fail(f"Erro inesperado: {str(e)}")
            print(f"Erro inesperado: {str(e)}")
            
    def test_kwai_empty_data(self):
        """
        Testa a criação de uma campanha com dados vazios.
        """
        response = self.client.post(self.create_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data) 
        self.assertIn("campaigns", response.data) 
        
        self.assertEqual(
            response.data["name"][0],
            "Este campo é obrigatório."
        ) 
        self.assertEqual(
            response.data["campaigns"][0],
            "Este campo é obrigatório."
        )    

    def test_html_injection_kwai_title(self):
        """
        Testa a criação de uma campanha com injeção de código HTML no campo 'title'.
        """
        payload = {
            "name": "<script>alert('XSS')</script>",
            "campaigns": [{"uid": self.campaign_uid}],
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["name"][0],
            "O campo não pode conter tags HTML."
        )
    
    def test_xrss_attack_kwai_title(self):
        """
        Testa a criação de uma campanha com ataque XSS no campo 'title'.
        """
        payload = {
            "name": "&lt;script&gt;alert(&#x27;XRSS&#x27;);&lt;/script&gt;",
            "campaigns": [{"uid": self.campaign_uid}],
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["name"][0],
            "O campo não pode conter tags HTML."
        )
    
    def test_xrss_attack_kwai_emoji(self):
        """
         Testa a criação de uma campanha com Emoji no campo 'title'.
        """
        payload = {
            "name": "😀",
            "campaigns": [{"uid": self.campaign_uid}],
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["name"][0],
            "O campo só pode conter caracteres ASCII."
        )
        
    def test_kwai_title_too_short(self):
        """
        Testa a criação de uma campanha com o título muito curto.
        """
        payload = {
            "name": "A",
            "campaigns": [{"uid": self.campaign_uid}],
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["name"][0],
            "O campo deve ter pelo menos 5 caracteres."
        )
    
    def test_kwai_title_too_long(self):
        """
        Testa a criação de uma campanha com o título muito longo.
        """
        payload = {
            "name": "A" * 101,
            "campaigns": [{"uid": self.campaign_uid}],
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["name"][0],
            "Certifique-se de que este campo não tenha mais de 100 caracteres."
        )
     
    def test_kwai_invalid_integration(self):
        """
        Testa a criação de uma campanha com uma integração inválida.
        """
        payload = {
            "name": namecampaign,
            "campaigns": [{"uid": 'INVALID_INTEGRATION'}],
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("campaigns", response.data)
        self.assertEqual(
            response.data["campaigns"][0]['uid'][0],
            'Must be a valid UUID.'
        )
        
    def test_kwai_duplicate_campaign_uid(self):
        """
        Testa a criação de um Kwai com a mesma campanha já utilizada.
        """
        # Primeiro Kwai com a campanha
        payload_1 = {
            "name": "Primeiro Kwai",
            "campaigns": [{"uid": self.campaign_uid}],
        }
        response_1 = self.client.post(self.create_url, payload_1, format="json")
        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)
        self.assertIn("uid", response_1.data)
        self.assertEqual(response_1.data["name"], "Primeiro Kwai")

        # Segundo Kwai com a mesma campanha
        payload_2 = {
            "name": "Segundo Kwai",
            "campaigns": [{"uid": self.campaign_uid}],
        }
        response_2 = self.client.post(self.create_url, payload_2, format="json")
        self.assertEqual(response_2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("campaigns", response_2.data)
        self.assertEqual(response_2.data["campaigns"], "A campanha já está em uso.")
        
    def test_kwai_successful_creation(self):
        """
        Testa a criação bem-sucedida de uma conta Kwai.
        """
        payload = {
            "name": "Conta Kwai Teste",
            "campaigns": [{"uid": self.campaign_uid}],
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("uid", response.data)
        self.assertIn("name", response.data)
        self.assertIn("campaigns", response.data)
        self.assertEqual(response.data["name"], "Conta Kwai Teste")
        self.assertEqual(len(response.data["campaigns"]), 1)
        self.assertEqual(response.data["campaigns"][0]["uid"], self.campaign_uid)
    
