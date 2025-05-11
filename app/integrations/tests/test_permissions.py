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


class TestIntegrationAccessPermissions(APITestCase):
    
    def setUp(self):
        try:
            # Criar o primeiro usuário
            self.register_url = reverse("account-create-list")
            self.login_url = reverse("login")
            self.integration_url = reverse("integration-list")
            
            payload_user1 = {"email": "isadora_mariane_damata@gmail.com", "cpf": "23953129163", "name": "Isadora Mariane Ayla da Mata",
                             "password": password, "confirm_password": password}
            reg_response = self.client.post(self.register_url, payload_user1, format="json")
            self.assertEqual(reg_response.status_code, status.HTTP_201_CREATED)

            # Autenticar o primeiro usuário
            login_payload_user1 = {"identifier": "isadora_mariane_damata@gmail.com", "password": password}
            login_response_user1 = self.client.post(self.login_url, login_payload_user1, format="json")
            self.assertEqual(login_response_user1.status_code, status.HTTP_200_OK)
            self.access_token_user1 = login_response_user1.data.get("access")
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token_user1}")

            # Criar uma integração para o primeiro usuário
            integration_payload = {"gateway": gateway, "name": nameIntegration}
            create_response = self.client.post(self.integration_url, integration_payload, format="json")
            self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
            self.integration_uid = create_response.data["uid"]
            self.detail_url = reverse("integration-detail", kwargs={"uid": self.integration_uid})
            self.update_url = reverse("integration-list") + self.integration_uid + "/" 
            self.delete_url = reverse("integration-list") + self.integration_uid + "/" 
            # Criar o segundo usuário
            payload_user2 = {"email": email, "cpf": cpf, "name": name,
                             "password": password, "confirm_password": password}
            reg_response = self.client.post(self.register_url, payload_user2, format="json")
            self.assertEqual(reg_response.status_code, status.HTTP_201_CREATED)

            # Autenticar o segundo usuário
            login_payload_user2 = {"identifier": email, "password": password}
            login_response_user2 = self.client.post(self.login_url, login_payload_user2, format="json")
            self.assertEqual(login_response_user2.status_code, status.HTTP_200_OK)
            self.access_token_user2 = login_response_user2.data.get("access")
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token_user2}")

        except Exception as e:
            self.fail(f"Erro inesperado no setup: {str(e)}")

    def test_access_integration_of_another_user(self):
        """
        Testa se um usuário consegue acessar os dados de integração de outro usuário.
        """
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
      
    def test_edit_integration_of_another_user(self):
        """
        Testa se um usuário consegue editar os dados de integração de outro usuário.
        """
        payload = {"gateway": gateway, "name": "Novo Nome"}
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_integration_of_another_user(self):
        """
        Testa se um usuário consegue excluir a integração de outro usuário.
        """
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)