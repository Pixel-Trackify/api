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
            integration_payload = {"gateway": "disrupty", "name": "Conta da Sarah - Disrupty"}
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
        self.assertEqual(response.data["name"], "Conta da Sarah - Disrupty")
        self.assertEqual(response.data["gateway"], "disrupty")
        self.assertEqual(response.data["status"], "active")
        self.assertTrue(response.data["webhook_url"].startswith("http"))
        self.assertIn("disrupty", response.data["webhook_url"])
        self.assertIn(str(self.integration_uid), response.data["webhook_url"])