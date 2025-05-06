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

"""
@todo:
    - Testar com todos os gateways disponíveis
"""
class TestIntegrationRegistration(APITestCase):
    
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
            
            self.create_url = reverse("integration-list")
        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {str(e)}")
            print(f"Rota não encontrada: {str(e)}")
        except Exception as e:
            self.fail(f"Erro inesperado: {str(e)}")
            print(f"Erro inesperado: {str(e)}")
            
    def test_create_integration_invalid_name(self):
        """
        Testa a criação de uma integração com um nome de gateway inválido.
        """
        invalid_payload = {
            "gateway": "zeroonea",  # Valor inválido
            "name": "Teste"
        }
        response = self.client.post(self.create_url, invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("gateway", response.data)
        self.assertEqual(
            response.data["gateway"][0],
            "\"zeroonea\" não é um escolha válido."
        )
        
    def test_create_integration_html_injection(self):
        """
        Testa a criação de uma integração com injeção de código HTML no campo 'name'.
        """
        payload = {
            "gateway": gateway,
            "name": "<script>alert('XSS')</script>"
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["name"][0],
            "O nome contém caracteres inválidos."
        )
        
    def test_create_integration_name_too_long(self):
        """
        Testa a criação de uma integração com um nome maior que 200 caracteres.
        """
        long_name = "A" * 201
        payload = {
            "gateway": gateway,
            "name": long_name
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["name"][0],
            "Certifique-se de que este campo não tenha mais de 100 caracteres."
        )
    
    def test_create_integration(self):
        """
        Testa a criação de uma nova integração.
        """
        payload = {
            "gateway": gateway,
            "name": nameIntegration
        }
        response = self.client.post(self.create_url, payload, format="json")
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

class TestIntegrationUpdate(APITestCase):
    
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
            # Autenticar para obter token
            login_payload = {"identifier": email, "password": password}
            login_response = self.client.post(self.login_url, login_payload, format="json")
            self.assertEqual(login_response.status_code, status.HTTP_200_OK)
            self.access_token = login_response.data.get("access")
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
            # Criar uma integração para atualizar
            integration_payload = {"gateway": gateway, "name": nameIntegration}
            create_response = self.client.post(self.create_url, integration_payload, format="json")
            self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
            self.integration_uid = create_response.data["uid"]
            self.update_url = reverse("integration-list") + self.integration_uid + "/" 
        except Exception as e:
            self.fail(f"Erro inesperado no setup: {str(e)}")

    def test_update_integration_invalid_name(self):
        """
        Testa a atualização de uma integração com um nome de gateway inválido.
        """
        invalid_payload = {
            "gateway": "zeroonea",
            "name": "Teste Atualizado"
        }
        response = self.client.put(self.update_url, invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("gateway", response.data)
        self.assertEqual(
            response.data["gateway"][0],
            "\"zeroonea\" não é um escolha válido."
        )

    def test_update_integration_html_injection(self):
        """
        Testa a atualização de uma integração com injeção de código HTML no campo 'name'.
        """
        payload = {
            "gateway": gateway,
            "name": "<script>alert('XSS')</script>"
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["name"][0],
            "O nome contém caracteres inválidos."
        )

    def test_update_integration_name_too_long(self):
        """
        Testa a atualização de uma integração com um nome maior que 200 caracteres.
        """
        long_name = "A" * 201
        payload = {
            "gateway": gateway,
            "name": long_name
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["name"][0],
            "Certifique-se de que este campo não tenha mais de 100 caracteres."
        )

    def test_update_integration(self):
        """
        Testa a atualização de uma integração com dados válidos.
        """
        updated_name = "Conta Atualizada - ZeroOne"
        payload = {
            "gateway": gateway,
            "name": updated_name
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], updated_name)
        self.assertEqual(response.data["gateway"], gateway)

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

class TestIntegrationListing(APITestCase):
    
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
            # Autenticar para obter token
            login_payload = {"identifier": email, "password": password}
            login_response = self.client.post(self.login_url, login_payload, format="json")
            self.assertEqual(login_response.status_code, status.HTTP_200_OK)
            self.access_token = login_response.data.get("access")
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
            # Criar duas integrações para listar
            integration_payload_1 = {"gateway": gateway, "name": "Zero"}
            integration_payload_2 = {"gateway": "disrupty", "name": "Teste"}
            self.client.post(self.create_url, integration_payload_1, format="json")
            self.client.post(self.create_url, integration_payload_2, format="json")
        except Exception as e:
            self.fail(f"Erro inesperado no setup: {str(e)}")

    def test_list_integrations(self):
        """
        Testa a listagem de integrações.
        """
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)

        # Verifica os dados da primeira integração
        integration_1 = response.data["results"][1]
        self.assertIn("uid", integration_1)
        self.assertEqual(integration_1["name"], "Zero")
        self.assertEqual(integration_1["gateway"], gateway)
        self.assertFalse(integration_1["deleted"])
        self.assertEqual(integration_1["status"], "active")
        self.assertTrue(integration_1["webhook_url"].startswith("http"))

        # Verifica os dados da segunda integração
        integration_2 = response.data["results"][0]
        self.assertIn("uid", integration_2)
        self.assertEqual(integration_2["name"], "Teste")
        self.assertEqual(integration_2["gateway"], "disrupty")
        self.assertFalse(integration_2["deleted"])
        self.assertEqual(integration_2["status"], "active")
        self.assertTrue(integration_2["webhook_url"].startswith("http"))
        
    def test_list_integrations_with_search_filter(self):
        """
        Testa a listagem de integrações com o filtro de busca (?search).
        """
        # Filtrar integrações pelo nome "Zero"
        response = self.client.get(f"{self.create_url}?search=Zero")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)

        # Verifica os dados da integração retornada
        integration = response.data["results"][0]
        self.assertIn("uid", integration)
        self.assertEqual(integration["name"], "Zero")
        self.assertEqual(integration["gateway"], gateway)
        self.assertEqual(integration["status"], "active")
        self.assertTrue(integration["webhook_url"].startswith("http"))

class TestIntegrationDetail(APITestCase):
    
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
            # Autenticar para obter token
            login_payload = {"identifier": email, "password": password}
            login_response = self.client.post(self.login_url, login_payload, format="json")
            self.assertEqual(login_response.status_code, status.HTTP_200_OK)
            self.access_token = login_response.data.get("access")
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
            # Criar uma integração para detalhes
            integration_payload = {"gateway": "disrupty", "name": "Dis"}
            create_response = self.client.post(self.create_url, integration_payload, format="json")
            self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
            self.integration_uid = create_response.data["uid"]
            self.detail_url = reverse("integration-detail", kwargs={"uid": self.integration_uid})
        except Exception as e:
            self.fail(f"Erro inesperado no setup: {str(e)}")

    def test_integration_detail(self):
        """
        Testa a visualização dos detalhes de uma integração.
        """
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("uid", response.data)
        self.assertEqual(response.data["uid"], self.integration_uid)
        self.assertEqual(response.data["name"], "Dis")
        self.assertEqual(response.data["gateway"], "disrupty")
        self.assertEqual(response.data["status"], "active")
        self.assertTrue(response.data["webhook_url"].startswith("http"))
        self.assertIn("disrupty", response.data["webhook_url"])
        self.assertIn(str(self.integration_uid), response.data["webhook_url"])