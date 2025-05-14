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

class TestCampaignUpdate(APITestCase):
    
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
            
            self.update_url = reverse("campaign-detail", kwargs={"uid": self.campaign_uid})
            
        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {str(e)}")
            print(f"Rota não encontrada: {str(e)}")
        except Exception as e:
            self.fail(f"Erro inesperado: {str(e)}")
            print(f"Erro inesperado: {str(e)}")
            
    def test_campaign_empty_data(self):
        """
        Testa a criação de uma campanha com dados vazios.
        """
        response = self.client.put(self.update_url, {}, format="json")
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
        
    def test_campaign_empty_CPC(self):
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
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("CPC", response.data)
        self.assertEqual(
            response.data["CPC"][0],
            "Este campo é obrigatório."
        )
    
    def test_campaign_invalid_CPV(self):
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
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("CPV", response.data)
        self.assertEqual(
            response.data["CPV"][0],
            "Este campo é obrigatório."
        )
    
    def test_campaign_invalid_CPM(self):
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
        response = self.client.put(self.update_url, payload, format="json")
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
        response = self.client.put(self.update_url, payload, format="json")
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
        response = self.client.put(self.update_url, payload, format="json")
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
        response = self.client.put(self.update_url, payload, format="json")
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
        response = self.client.put(self.update_url, payload, format="json")
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
        response = self.client.put(self.update_url, payload, format="json")
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
        response = self.client.put(self.update_url, payload, format="json")
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
        response = self.client.put(self.update_url, payload, format="json")
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
        response = self.client.put(self.update_url, payload, format="json")
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
        response = self.client.put(self.update_url, payload, format="json")
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
        response = self.client.put(self.update_url, payload, format="json")
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
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("method", response.data)
        self.assertEqual(
            response.data["method"][0],
             '"INVALID_METHOD" não é um escolha válido.'
        )
        
    def test_campaign_invalid_integration(self):
        """
        Testa a criação de uma campanha com uma integração inválida.
        """
        payload = {
            "title": namecampaign,
            "description": descriptionCampaign,
            "integrations": ["INVALID_INTEGRATION"],
            "method": methodCampaign,
            "CPC": amountCampaign
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("integrations", response.data)
        self.assertEqual(
            response.data["integrations"][0],
            'O valor “INVALID_INTEGRATION” não é um UUID válido'
        )
    
    def test_campaign_not_found_uid_integration(self):
        """
        Testa a criação de uma campanha com uma integração que não existe.
        """
        payload = {
            "title": namecampaign,
            "description": descriptionCampaign,
            "integrations": ["00000000-0000-0000-0000-000000000000"],
            "method": methodCampaign,
            "CPC": amountCampaign
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("integrations", response.data)
        self.assertEqual(
            response.data["integrations"][0],
            'Integração não foi encontrada.'
        )
        
    def test_campaign_invalid_CPC(self):
        """
        Testa a criação de uma campanha com um CPC inválido.
        """
        payload = {
            "title": namecampaign,
            "description": descriptionCampaign,
            "integrations": [self.uid_integration],
            "method": methodCampaign,
            "CPC": -1
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("CPC", response.data)
        self.assertEqual(
            response.data["CPC"][0],
            "Este campo deve ser maior que zero."
        )
    
    def test_campaign_invalid_CPV(self):
        """
        Testa a criação de uma campanha com um CPV inválido.
        """
        payload = {
            "title": namecampaign,
            "description": descriptionCampaign,
            "integrations": [self.uid_integration],
            "method": "CPV",
            "CPV": -1
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("CPV", response.data)
        self.assertEqual(
            response.data["CPV"][0],
            "Este campo deve ser maior que zero."
        )
        
    def test_campaign_invalid_CPM(self):
        """
        Testa a criação de uma campanha com um CPM inválido.
        """
        payload = {
            "title": namecampaign,
            "description": descriptionCampaign,
            "integrations": [self.uid_integration],
            "method": "CPM",
            "CPM": -1
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("CPM", response.data)
        self.assertEqual(
            response.data["CPM"][0],
            "Este campo deve ser maior que zero."
        )
    
    def test_campaign_invalid_CPC_type(self):
        """
        Testa a criação de uma campanha com um CPC inválido (não numérico).
        """
        payload = {
            "title": namecampaign,
            "description": descriptionCampaign,
            "integrations": [self.uid_integration],
            "method": methodCampaign,
            "CPC": "invalid"
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("CPC", response.data)
        self.assertEqual(
            response.data["CPC"][0],
            "Um número válido é necessário."
        )
        
    def test_campaign_invalid_CPV_type(self):
        """
        Testa a criação de uma campanha com um CPV inválido (não numérico).
        """
        payload = {
            "title": namecampaign,
            "description": descriptionCampaign,
            "integrations": [self.uid_integration],
            "method": "CPV",
            "CPV": "invalid"
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("CPV", response.data)
        self.assertEqual(
            response.data["CPV"][0],
            "Um número válido é necessário."
        )
        
    def test_campaign_invalid_CPM_type(self):
        """
        Testa a criação de uma campanha com um CPM inválido (não numérico).
        """
        payload = {
            "title": namecampaign,
            "description": descriptionCampaign,
            "integrations": [self.uid_integration],
            "method": "CPM",
            "CPM": "invalid"
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("CPM", response.data)
        self.assertEqual(
            response.data["CPM"][0],
            "Um número válido é necessário."
        )
     
    def test_campaign_with_deleted_integration(self):
        """
        Testa a criação de uma campanha com uma integração que foi deletada.
        """
        # Criar uma integração
        integration_payload = {
            "gateway": gateway,
            "name": "Integração Deletada"
        }
        integration_response = self.client.post(reverse("integration-list"), integration_payload, format="json")
        self.assertEqual(integration_response.status_code, status.HTTP_201_CREATED)
        deleted_integration_uid = integration_response.data.get("uid")

        # Deletar a integração
        delete_url = reverse("integration-list") + deleted_integration_uid + "/"
        delete_response = self.client.delete(delete_url, format="json")
        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)

        # Tentar criar uma campanha com a integração deletada
        payload = {
            "title": namecampaign,
            "description": descriptionCampaign,
            "integrations": [deleted_integration_uid],
            "method": methodCampaign,
            "CPC": amountCampaign
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("integrations", response.data)
        self.assertEqual(
            response.data["integrations"][0],
            "Integração não foi encontrada."
        )
        
    def test_campaign_with_integration_in_use(self):
        """
        Testa a criação de uma campanha usando uma integração que já está em uso em outra campanha.
        """
        # Criar uma integração
        integration_payload = {
            "gateway": gateway,
            "name": "Integração Em Uso"
        }
        integration_response = self.client.post(reverse("integration-list"), integration_payload, format="json")
        self.assertEqual(integration_response.status_code, status.HTTP_201_CREATED)
        integration_uid = integration_response.data.get("uid")

        # Criar uma campanha usando essa integração
        campaign_payload = {
            "title": "Campanha Original",
            "description": "Descrição da campanha original",
            "integrations": [integration_uid],
            "method": methodCampaign,
            "CPC": amountCampaign
        }
        campaign_response = self.client.post(self.create_url, campaign_payload, format="json")
        self.assertEqual(campaign_response.status_code, status.HTTP_201_CREATED)

        # Tentar criar outra campanha usando a mesma integração
        new_campaign_payload = {
            "title": "Campanha Nova",
            "description": "Descrição da nova campanha",
            "integrations": [integration_uid],
            "method": methodCampaign,
            "CPC": amountCampaign
        }
        new_campaign_response = self.client.put(self.update_url, new_campaign_payload, format="json")
        self.assertEqual(new_campaign_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("integrations", new_campaign_response.data)
        self.assertEqual(
            new_campaign_response.data["integrations"][0],
            f"A Integração '{integration_response.data['name']}' já está em uso."
        )
        
    def test_campaign_CPC(self):
        """
        Testa a criação de uma nova campanha CPC.
        """
        payload = {
            "title": "Campanha CPC Teste",
            "description": "Descrição da campanha CPC",
            "integrations": [self.uid_integration],
            "method": "CPC",
            "CPC": 1.99
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("uid", response.data)
        self.assertIn("title", response.data)
        self.assertIn("description", response.data)
        self.assertIn("CPC", response.data)
        
        self.assertEqual(response.data["title"], "Campanha CPC Teste")
        self.assertEqual(response.data["description"], "Descrição da campanha CPC")
        self.assertEqual(response.data["CPC"], str(1.99))
        self.assertTrue(UUID(response.data["uid"], version=4))

    def test_campaign_CPV(self):
        """
        Testa a criação de uma nova campanha CPV.
        """
        payload = {
            "title": "Campanha CPV Teste",
            "description": "Descrição da campanha CPV",
            "integrations": [self.uid_integration],
            "method": "CPV",
            "CPV": 2.75
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("uid", response.data)
        self.assertIn("title", response.data)
        self.assertIn("method", response.data)
        self.assertIn("description", response.data)
        self.assertIn("CPV", response.data)
        
        self.assertEqual(response.data["title"], "Campanha CPV Teste")
        self.assertEqual(response.data["description"], "Descrição da campanha CPV")
        self.assertEqual(response.data["method"], "CPV")
        self.assertEqual(response.data["CPV"], str(2.75))
        self.assertTrue(UUID(response.data["uid"], version=4))
        
    def test_campaign_CPM(self):
        """
        Testa a criação de uma nova campanha CPM.
        """
        payload = {
            "title": "Campanha CPM Teste",
            "description": "Descrição da campanha CPM",
            "integrations": [self.uid_integration],
            "method": "CPM",
            "CPM": 3.99
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("uid", response.data)
        self.assertIn("title", response.data)
        self.assertIn("method", response.data)
        self.assertIn("description", response.data)
        self.assertIn("CPM", response.data)
        
        self.assertEqual(response.data["title"], "Campanha CPM Teste")
        self.assertEqual(response.data["description"], "Descrição da campanha CPM")
        self.assertEqual(response.data["method"], "CPM")
        self.assertEqual(response.data["CPM"], str(3.99))
        self.assertTrue(UUID(response.data["uid"], version=4))
